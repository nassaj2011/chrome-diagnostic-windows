from chrome_diagnostic.models import DiagnosticResult, PerformanceSample, RunMetadata
from chrome_diagnostic.report import build_summary


def test_summary_detects_whea_and_cpu():
    result = DiagnosticResult(
        metadata=RunMetadata(version="1.0.0", started_at="2026-01-01T00:00:00+00:00"),
        samples=[
            PerformanceSample(
                timestamp="x",
                elapsed_seconds=1,
                phase="AfterChromeLaunch",
                system_cpu_percent=95,
                chrome_cpu_percent=61,
                chrome_process_count=10,
                chrome_working_set_mb=1200,
                memory_used_percent=50,
                memory_available_mb=8000,
                disk_read_mbps=2,
                disk_write_mbps=1,
            )
        ],
    )
    summary = build_summary(result, [], [{"PrimaryDeviceName": "PCI\\VEN_1234"}])
    assert summary["system_cpu_peak_percent"] == 95
    assert summary["chrome_cpu_peak_percent"] == 61
    assert summary["whea_event_17_count_24h"] == 1
    assert any("WHEA" in item for item in summary["observations"])
