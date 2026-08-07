from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PerformanceSample:
    timestamp: str
    elapsed_seconds: float
    phase: str
    system_cpu_percent: float
    chrome_cpu_percent: float
    chrome_process_count: int
    chrome_working_set_mb: float
    memory_used_percent: float
    memory_available_mb: float
    disk_read_mbps: float
    disk_write_mbps: float


@dataclass(slots=True)
class TopProcessSample:
    timestamp: str
    elapsed_seconds: float
    rank: int
    name: str
    pid: int
    cpu_percent: float
    working_set_mb: float


@dataclass(slots=True)
class RunMetadata:
    version: str
    started_at: str
    chrome_detected_at: str | None = None
    completed_at: str | None = None
    baseline_seconds: int = 5
    capture_seconds: int = 60
    sample_interval_ms: int = 250
    report_directory: str = ""


@dataclass(slots=True)
class DiagnosticResult:
    metadata: RunMetadata
    samples: list[PerformanceSample] = field(default_factory=list)
    top_processes: list[TopProcessSample] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "metadata": asdict(self.metadata),
            "summary": self.summary,
            "samples": [asdict(x) for x in self.samples],
            "top_processes": [asdict(x) for x in self.top_processes],
        }


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
