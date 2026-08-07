from __future__ import annotations

import shutil
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .chrome import dataclass_rows
from .models import DiagnosticResult
from .utils import write_csv, write_json, write_text


def _max(values: list[float]) -> float:
    return round(max(values), 1) if values else 0.0


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


def build_summary(result: DiagnosticResult, extensions: list[object], whea: list[dict[str, Any]]) -> dict[str, Any]:
    after = [s for s in result.samples if s.phase == "AfterChromeLaunch"]
    cpu = [s.system_cpu_percent for s in after]
    chrome_cpu = [s.chrome_cpu_percent for s in after]
    chrome_mem = [s.chrome_working_set_mb for s in after]
    mem_used = [s.memory_used_percent for s in after]
    mem_available = [s.memory_available_mb for s in after]
    disk_read = [s.disk_read_mbps for s in after]
    disk_write = [s.disk_write_mbps for s in after]
    device_counts = Counter(str(e.get("PrimaryDeviceName") or "unknown") for e in whea)

    saturation_samples = sum(1 for value in cpu if value >= 90)
    summary = {
        "valid_samples": len(after),
        "system_cpu_peak_percent": _max(cpu),
        "system_cpu_average_percent": _avg(cpu),
        "chrome_cpu_peak_percent": _max(chrome_cpu),
        "chrome_cpu_average_percent": _avg(chrome_cpu),
        "chrome_ram_peak_mb": _max(chrome_mem),
        "chrome_process_peak": max((s.chrome_process_count for s in after), default=0),
        "memory_used_peak_percent": _max(mem_used),
        "memory_available_min_mb": round(min(mem_available), 1) if mem_available else 0.0,
        "disk_read_peak_mbps": _max(disk_read),
        "disk_write_peak_mbps": _max(disk_write),
        "cpu_saturation_samples": saturation_samples,
        "installed_extension_entries": len(extensions),
        "whea_event_17_count_24h": len(whea),
        "whea_primary_devices": dict(device_counts.most_common()),
        "observations": [],
    }

    observations: list[str] = summary["observations"]
    if summary["system_cpu_peak_percent"] >= 90:
        observations.append("System CPU reached 90% or higher during Chrome capture.")
    if summary["chrome_cpu_peak_percent"] >= 50:
        observations.append("Chrome showed a high aggregate CPU burst during capture.")
    if summary["memory_available_min_mb"] and summary["memory_available_min_mb"] < 1024:
        observations.append("Available physical memory dropped below 1 GB.")
    if len(extensions) >= 15:
        observations.append("A relatively large number of extension installations were found across Chrome profiles.")
    if whea:
        observations.append(f"Windows recorded {len(whea)} corrected PCIe WHEA Event ID 17 event(s) in the last 24 hours.")
    if not observations:
        observations.append("No single threshold-based bottleneck was identified. Review the timeline for short spikes and correlations.")
    return summary


def write_reports(
    report_dir: Path,
    result: DiagnosticResult,
    system_info: dict[str, Any],
    defender: dict[str, Any],
    whea: list[dict[str, Any]],
    pcie: list[dict[str, Any]],
    extensions: list[object],
    chrome_processes: list[object],
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    result.summary = build_summary(result, extensions, whea)

    write_csv(
        report_dir / "Performance-Samples.csv",
        [asdict(x) for x in result.samples],
        list(asdict(result.samples[0]).keys()) if result.samples else [],
    )
    write_csv(
        report_dir / "Top-Processes.csv",
        [asdict(x) for x in result.top_processes],
        list(asdict(result.top_processes[0]).keys()) if result.top_processes else [],
    )

    ext_rows = dataclass_rows(extensions)
    write_csv(
        report_dir / "Chrome-Extensions.csv",
        ext_rows,
        ["profile", "extension_id", "name", "version", "manifest_version"],
    )
    chrome_rows = dataclass_rows(chrome_processes)
    write_csv(
        report_dir / "Chrome-Processes.csv",
        chrome_rows,
        ["pid", "parent_pid", "process_type", "profile_directory", "is_extension_process", "working_set_mb", "created_at"],
    )

    write_json(report_dir / "System-Info.json", system_info)
    write_json(report_dir / "Defender-Status.json", defender)
    write_json(report_dir / "WHEA-Events.json", whea)
    write_json(report_dir / "PCIe-Devices.json", pcie)
    write_json(report_dir / "report.json", result.as_dict())

    lines = [
        "Chrome Diagnostic for Windows",
        f"Version: {result.metadata.version}",
        f"Started: {result.metadata.started_at}",
        f"Chrome detected: {result.metadata.chrome_detected_at or 'not detected'}",
        f"Completed: {result.metadata.completed_at or ''}",
        "",
        "=== Key measurements ===",
        f"System CPU: peak {result.summary['system_cpu_peak_percent']}% | average {result.summary['system_cpu_average_percent']}%",
        f"Chrome CPU: peak {result.summary['chrome_cpu_peak_percent']}% | average {result.summary['chrome_cpu_average_percent']}%",
        f"Chrome RAM peak: {result.summary['chrome_ram_peak_mb']} MB",
        f"Chrome process peak: {result.summary['chrome_process_peak']}",
        f"Memory: peak used {result.summary['memory_used_peak_percent']}% | minimum available {result.summary['memory_available_min_mb']} MB",
        f"Disk: peak read {result.summary['disk_read_peak_mbps']} MB/s | peak write {result.summary['disk_write_peak_mbps']} MB/s",
        f"Installed extension entries: {result.summary['installed_extension_entries']}",
        f"WHEA Event ID 17 (24h): {result.summary['whea_event_17_count_24h']}",
        "",
        "=== Automated observations ===",
        *[f"- {x}" for x in result.summary["observations"]],
        "",
        "Privacy: Chrome-Processes.csv intentionally excludes full command lines and URLs.",
        "Reports remain local unless you choose to share the ZIP.",
    ]
    write_text(report_dir / "Summary.txt", "\n".join(lines) + "\n")

    zip_path = report_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(str(report_dir), "zip", root_dir=report_dir)
    return zip_path
