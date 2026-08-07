# Chrome Diagnostic for Windows

[![CI](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/ci.yml)
[![Windows Build](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/build.yml/badge.svg)](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/build.yml)
[![Latest Release](https://img.shields.io/github/v/release/nassaj2011/chrome-diagnostic-windows?display_name=tag)](https://github.com/nassaj2011/chrome-diagnostic-windows/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A privacy-first Windows desktop utility for diagnosing **Chrome startup CPU spikes**, memory growth, process fan-out, extension overhead, and **WHEA / PCIe corrected hardware warnings**.

> Unofficial project. Not affiliated with or endorsed by Google. See [NOTICE.md](NOTICE.md).

[راهنمای فارسی](README.fa.md)

## Download

For most users, the recommended option is the Windows installer from the latest GitHub Release:

**[Download the latest release](https://github.com/nassaj2011/chrome-diagnostic-windows/releases/latest)**

Release assets include:

- `Chrome-Diagnostic-Setup-vX.Y.Z.exe` — standard Windows installer/uninstaller
- `ChromeDiagnostic.exe` — portable executable
- `SHA256SUMS.txt` — SHA-256 checksums for release verification

> Until the project has a code-signing certificate, Windows SmartScreen may show an **Unknown publisher** warning. Do not disable SmartScreen or Microsoft Defender. Verify the release checksum when needed.

## What problem does it solve?

A common Windows symptom is:

> Chrome opens, the PC becomes sluggish, CPU briefly jumps toward 100%, then the spike disappears before Task Manager makes the cause obvious.

Chrome Diagnostic captures that startup window at high frequency and packages the evidence into a local ZIP report.

It can help separate several common categories of problems:

- Chrome or renderer CPU bursts
- extension-related startup overhead
- memory and process-count growth
- another Windows process competing with Chrome
- storage activity during startup
- WHEA / PCIe warnings that may point to an independent driver, power-management, firmware, controller, link, or hardware issue

The tool is a **read-only diagnostic collector**. It does not change Chrome settings, drivers, BIOS, Windows power plans, or PCIe configuration.

## Highlights

- 5-second clean baseline with Chrome closed
- Manual Chrome launch only — no fragile browser automation
- 250 ms startup sampling to catch short CPU spikes
- System CPU, Chrome CPU, Chrome RAM, process count, available RAM and disk throughput
- Top CPU processes during the capture
- Privacy-reduced Chrome process snapshot — **no full command lines or browsing URLs**
- Chrome extension inventory by profile
- Microsoft Defender status
- WHEA Event ID 17 collection for the last 24 hours
- PCI/PCIe device and driver inventory
- Local `Summary.txt`, CSV/JSON data and ZIP package
- No telemetry, no cloud upload and no account required
- Standard Windows installer/uninstaller
- Portable executable available in each release

## Supported systems

- Windows 10 x64
- Windows 11 x64
- Google Chrome desktop

The source uses Python 3.11+ and `psutil`. End users do **not** need Python when using a packaged release.

## Quick start

1. Install **Chrome Diagnostic** from the latest GitHub Release.
2. Close every Chrome window.
3. Start Chrome Diagnostic.
4. Click **Start diagnostic**.
5. Keep Chrome closed during the 5-second baseline.
6. When the application shows **OPEN CHROME NOW**, launch Chrome using the shortcut you normally use.
7. Continue using Chrome normally during the 60-second capture.
8. Review the generated report under:

```text
Documents\Chrome Diagnostic Reports
```

## Report contents

| File | Purpose |
|---|---|
| `Summary.txt` | Human-readable measurements and threshold observations |
| `Performance-Samples.csv` | High-frequency startup timeline |
| `Top-Processes.csv` | Top CPU consumers over time |
| `Chrome-Processes.csv` | Privacy-reduced Chrome process metadata |
| `Chrome-Extensions.csv` | Installed extension entries by profile |
| `System-Info.json` | OS, CPU, storage, GPU and power plan information |
| `Defender-Status.json` | Microsoft Defender status when available |
| `WHEA-Events.json` | Recent WHEA Event ID 17 records |
| `PCIe-Devices.json` | PCI/PCIe device and driver inventory |
| `report.json` | Machine-readable diagnostic summary and samples |

See [docs/REPORTS.md](docs/REPORTS.md) for details.

## Privacy

Chrome Diagnostic has **no telemetry** and does not upload reports anywhere. Reports remain on the local PC unless the user chooses to share them.

To reduce accidental disclosure, the public release does **not** save full Chrome command lines or browsing URLs. Reports may still contain hardware IDs, profile labels, extension IDs, driver versions and Windows event details.

**Review a diagnostic report before posting it publicly.**

Read [PRIVACY.md](PRIVACY.md).

## WHEA / PCIe notes

WHEA Event ID 17 means Windows reported a **corrected PCI Express hardware error**.

A corrected error does not by itself prove that hardware is failing. Repeated events can, however, be useful evidence while investigating:

- PCIe link stability
- controller or device drivers
- power-management transitions
- chipset / platform drivers
- BIOS / firmware
- connected devices
- hardware faults

Chrome Diagnostic records these warnings but does not modify the system.

## Known limitations

- The application currently targets Google Chrome on Windows.
- It is a diagnostic collector, not an automatic repair tool.
- Extension inventory shows installed entries; an extension's runtime impact still requires controlled A/B testing.
- Very short system activity can always be challenging to attribute perfectly, although the 250 ms startup sampler is designed to capture brief spikes.
- WHEA events may be unrelated to Chrome and should be interpreted separately unless timestamps and controlled testing show a correlation.
- Release binaries are not yet code-signed.

## Run from source

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m chrome_diagnostic
```

## Build a Windows release locally

Install Python 3.11+ and Inno Setup 6, then run:

```powershell
.\tools\build.ps1
```

Build output is placed in `dist/`.

## Development

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check src tests
```

Project documentation:

- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)
- [Report format](docs/REPORTS.md)
- [Release process](docs/RELEASE.md)
- [Contributing](CONTRIBUTING.md)

## Security

Please do not publish sensitive diagnostics in a public issue. Use the process described in [SECURITY.md](SECURITY.md) for security reports.

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting substantial changes.

## License

MIT — see [LICENSE](LICENSE).
