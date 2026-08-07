# Architecture

Chrome Diagnostic separates **fast startup sampling** from **slow static inventory**.

## Phase order

1. Verify Chrome is not running.
2. Start the low-overhead sampler immediately.
3. Capture a 5-second baseline.
4. Prompt the user to open Chrome manually.
5. Continue sampling while waiting, so the first `chrome.exe` activity is not missed.
6. Capture 60 seconds after Chrome is detected.
7. Only after the performance window ends, collect slower Windows inventory:
   - system/driver information,
   - Defender status,
   - WHEA Event ID 17,
   - PCIe devices,
   - Chrome extensions.
8. Build local reports and ZIP.

This ordering is intentional. Earlier prototypes gathered WMI/CIM inventory before sampling and could miss the first seconds of Chrome startup or perturb the measurement.

## Modules

- `app.py` — Tkinter UI and worker-thread coordination
- `collector.py` — diagnostic state machine
- `metrics.py` — fast `psutil` sampler
- `chrome.py` — Chrome process/profile/extension discovery
- `windows_diag.py` — read-only Windows diagnostics
- `report.py` — summary, CSV/JSON/text and ZIP generation
- `models.py` — typed report models

## Privacy boundary

`Chrome-Processes.csv` contains a reduced process model. The collector may inspect process arguments locally to determine process type/profile, but it does not persist full command lines or URLs.
