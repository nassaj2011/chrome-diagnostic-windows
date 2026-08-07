from __future__ import annotations

import time
from pathlib import Path
from threading import Event
from collections.abc import Callable

from . import __version__
from .chrome import chrome_is_running, scan_extensions, snapshot_chrome_processes
from .metrics import FastSampler
from .models import DiagnosticResult, RunMetadata, iso_now
from .report import write_reports
from .windows_diag import collect_defender_status, collect_pcie_devices, collect_system_info, collect_whea_events

StatusCallback = Callable[[str, float, str], None]


class ChromeStillRunningError(RuntimeError):
    pass


class ChromeNotDetectedError(RuntimeError):
    pass


def _sleep_to_interval(started: float, interval_seconds: float) -> None:
    remainder = interval_seconds - (time.perf_counter() - started)
    if remainder > 0:
        time.sleep(remainder)


def run_diagnostic(
    output_root: Path,
    status: StatusCallback,
    cancel: Event,
    baseline_seconds: int = 5,
    capture_seconds: int = 60,
    sample_interval_ms: int = 250,
    wait_for_chrome_seconds: int = 300,
) -> Path:
    if chrome_is_running():
        raise ChromeStillRunningError("Chrome is already running. Close all Chrome windows and background processes before starting.")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    report_dir = output_root / f"Chrome-Diagnostic-{stamp}"
    report_dir.mkdir(parents=True, exist_ok=True)
    metadata = RunMetadata(
        version=__version__,
        started_at=iso_now(),
        baseline_seconds=baseline_seconds,
        capture_seconds=capture_seconds,
        sample_interval_ms=sample_interval_ms,
        report_directory=str(report_dir),
    )
    result = DiagnosticResult(metadata=metadata)
    sampler = FastSampler()
    interval = sample_interval_ms / 1000.0
    run_started = time.perf_counter()

    # Phase 1: fast baseline. Expensive static inventory is intentionally deferred.
    status("baseline", 0.02, "Capturing a clean baseline. Keep Chrome closed…")
    baseline_started = time.perf_counter()
    while time.perf_counter() - baseline_started < baseline_seconds:
        if cancel.is_set():
            raise RuntimeError("Cancelled")
        tick = time.perf_counter()
        elapsed = time.perf_counter() - run_started
        sample, top = sampler.sample(elapsed, "Baseline")
        if sample.chrome_process_count > 0:
            raise ChromeStillRunningError("Chrome started during the baseline. Close Chrome completely and start the diagnostic again.")
        result.samples.append(sample)
        result.top_processes.extend(top)
        fraction = min(1.0, (time.perf_counter() - baseline_started) / baseline_seconds)
        status("baseline", 0.02 + fraction * 0.08, f"Baseline {fraction*100:.0f}% — keep Chrome closed")
        _sleep_to_interval(tick, interval)

    # Phase 2: user opens Chrome manually. The sampler keeps running, so the first spike is not missed.
    status("waiting", 0.10, "Baseline complete. Open Chrome now using your normal shortcut.")
    wait_started = time.perf_counter()
    detected = False
    while time.perf_counter() - wait_started < wait_for_chrome_seconds:
        if cancel.is_set():
            raise RuntimeError("Cancelled")
        tick = time.perf_counter()
        elapsed = time.perf_counter() - run_started
        sample, top = sampler.sample(elapsed, "WaitingForChrome")
        if sample.chrome_process_count > 0:
            sample.phase = "AfterChromeLaunch"
            detected = True
            metadata.chrome_detected_at = iso_now()
        result.samples.append(sample)
        result.top_processes.extend(top)
        if detected:
            break
        status("waiting", 0.10, "Open Chrome now. Waiting for chrome.exe…")
        _sleep_to_interval(tick, interval)

    if not detected:
        raise ChromeNotDetectedError("Chrome was not detected within five minutes.")

    # Phase 3: high-frequency capture for a real 60 seconds after detection.
    status("capture", 0.12, "Chrome detected. Capturing startup performance…")
    capture_started = time.perf_counter()
    while time.perf_counter() - capture_started < capture_seconds:
        if cancel.is_set():
            raise RuntimeError("Cancelled")
        tick = time.perf_counter()
        elapsed = time.perf_counter() - run_started
        sample, top = sampler.sample(elapsed, "AfterChromeLaunch")
        result.samples.append(sample)
        result.top_processes.extend(top)
        fraction = min(1.0, (time.perf_counter() - capture_started) / capture_seconds)
        status("capture", 0.12 + fraction * 0.68, f"Monitoring Chrome startup… {int(capture_seconds - (time.perf_counter()-capture_started))}s remaining")
        _sleep_to_interval(tick, interval)

    # Phase 4: static diagnostics after performance capture so they do not distort startup measurements.
    status("inventory", 0.82, "Collecting system and browser inventory…")
    def safe_collect(fn, fallback):
        try:
            return fn()
        except Exception as exc:
            return fallback(exc)

    chrome_rows = safe_collect(snapshot_chrome_processes, lambda exc: [])
    extensions = safe_collect(scan_extensions, lambda exc: [])
    system_info = safe_collect(collect_system_info, lambda exc: {"status": "unavailable", "error": str(exc)})

    status("inventory", 0.88, "Reading Defender and WHEA/PCIe diagnostics…")
    defender = safe_collect(collect_defender_status, lambda exc: {"status": "unavailable", "error": str(exc)})
    whea = safe_collect(lambda: collect_whea_events(24), lambda exc: [])
    pcie = safe_collect(collect_pcie_devices, lambda exc: [])

    metadata.completed_at = iso_now()
    status("report", 0.96, "Building local report package…")
    zip_path = write_reports(report_dir, result, system_info, defender, whea, pcie, extensions, chrome_rows)
    status("done", 1.0, "Diagnostic complete")
    return zip_path
