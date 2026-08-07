# Report format

## Performance-Samples.csv

High-frequency timeline fields:

- `timestamp`
- `elapsed_seconds`
- `phase` (`Baseline`, `WaitingForChrome`, `AfterChromeLaunch`)
- `system_cpu_percent`
- `chrome_cpu_percent`
- `chrome_process_count`
- `chrome_working_set_mb`
- `memory_used_percent`
- `memory_available_mb`
- `disk_read_mbps`
- `disk_write_mbps`

## Top-Processes.csv

Top CPU processes sampled during the run. CPU is normalized to total logical processor capacity.

## Chrome-Processes.csv

Privacy-reduced snapshot:

- PID / parent PID
- process type (`browser`, `renderer`, `gpu-process`, etc.)
- profile directory flag when present
- extension-process boolean
- working-set memory
- creation time

Full command lines and URLs are intentionally omitted.

## Chrome-Extensions.csv

Installed extension entries found under Chrome user profiles. This is an installation inventory, not a guarantee that every listed extension is currently enabled.

## WHEA-Events.json

Recent Windows WHEA Event ID 17 records from the System log. Repeated corrected errors are evidence for troubleshooting, not automatic proof of hardware failure.

## PCIe-Devices.json

Connected PCI/PCIe device inventory, location paths and driver information when Windows exposes them.
