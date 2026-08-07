from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

import psutil

from .models import PerformanceSample, TopProcessSample


@dataclass(slots=True)
class _ProcState:
    user: float
    system: float


class FastSampler:
    """Low-overhead sampler designed to capture short startup spikes."""

    def __init__(self, logical_processors: int | None = None) -> None:
        self.logical_processors = logical_processors or max(psutil.cpu_count(logical=True) or 1, 1)
        self._previous_time = time.perf_counter()
        self._previous_proc: dict[int, _ProcState] = {}
        self._previous_disk = psutil.disk_io_counters()
        self._previous_disk_time = self._previous_time
        psutil.cpu_percent(interval=None)
        self._prime_processes()

    def _prime_processes(self) -> None:
        for proc in psutil.process_iter(["pid"]):
            try:
                times = proc.cpu_times()
                self._previous_proc[proc.pid] = _ProcState(times.user, times.system)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def sample(self, elapsed: float, phase: str, top_n: int = 8) -> tuple[PerformanceSample, list[TopProcessSample]]:
        now_perf = time.perf_counter()
        interval = max(now_perf - self._previous_time, 0.001)
        self._previous_time = now_perf
        timestamp = datetime.now().astimezone().isoformat(timespec="milliseconds")

        system_cpu = round(psutil.cpu_percent(interval=None), 1)
        vm = psutil.virtual_memory()

        process_rows: list[tuple[float, str, int, float]] = []
        chrome_cpu = 0.0
        chrome_mem = 0.0
        chrome_count = 0
        current_states: dict[int, _ProcState] = {}

        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                times = proc.cpu_times()
                current = _ProcState(times.user, times.system)
                current_states[proc.pid] = current
                previous = self._previous_proc.get(proc.pid)
                cpu = 0.0
                if previous is not None:
                    delta = (current.user + current.system) - (previous.user + previous.system)
                    cpu = max(0.0, (delta / interval) * 100.0 / self.logical_processors)
                name = proc.info.get("name") or "unknown"
                memory = proc.info.get("memory_info")
                rss_mb = round((memory.rss if memory else 0) / (1024 * 1024), 1)
                process_rows.append((cpu, name, proc.pid, rss_mb))
                if name.lower() == "chrome.exe":
                    chrome_count += 1
                    chrome_cpu += cpu
                    chrome_mem += rss_mb
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self._previous_proc = current_states

        read_mbps = 0.0
        write_mbps = 0.0
        disk = psutil.disk_io_counters()
        if disk and self._previous_disk:
            disk_interval = max(now_perf - self._previous_disk_time, 0.001)
            read_mbps = max(0.0, (disk.read_bytes - self._previous_disk.read_bytes) / disk_interval / (1024 * 1024))
            write_mbps = max(0.0, (disk.write_bytes - self._previous_disk.write_bytes) / disk_interval / (1024 * 1024))
        self._previous_disk = disk
        self._previous_disk_time = now_perf

        sample = PerformanceSample(
            timestamp=timestamp,
            elapsed_seconds=round(elapsed, 3),
            phase=phase,
            system_cpu_percent=system_cpu,
            chrome_cpu_percent=round(chrome_cpu, 1),
            chrome_process_count=chrome_count,
            chrome_working_set_mb=round(chrome_mem, 1),
            memory_used_percent=round(vm.percent, 1),
            memory_available_mb=round(vm.available / (1024 * 1024), 1),
            disk_read_mbps=round(read_mbps, 2),
            disk_write_mbps=round(write_mbps, 2),
        )

        top = sorted(process_rows, key=lambda x: x[0], reverse=True)[:top_n]
        top_rows = [
            TopProcessSample(
                timestamp=timestamp,
                elapsed_seconds=round(elapsed, 3),
                rank=index + 1,
                name=name,
                pid=pid,
                cpu_percent=round(cpu, 1),
                working_set_mb=rss,
            )
            for index, (cpu, name, pid, rss) in enumerate(top)
            if cpu >= 0.1
        ]
        return sample, top_rows
