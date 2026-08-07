# Chrome Diagnostic for Windows

A privacy-first Windows desktop utility for diagnosing **Chrome startup CPU spikes**, memory growth, process fan-out, installed extensions, and **WHEA / PCIe corrected hardware warnings**.

> Unofficial project. Not affiliated with or endorsed by Google. See [NOTICE.md](NOTICE.md).

[راهنمای فارسی](README.fa.md)

## Why this exists

A common Windows symptom is: Chrome opens, the whole PC becomes sluggish, CPU briefly jumps toward 100%, then the spike disappears before Task Manager makes the cause obvious. Chrome Diagnostic captures the startup window at high frequency and packages the evidence into a local ZIP report.

The tool also collects Windows WHEA Event ID 17 and PCIe device inventory **after** the performance capture, so hardware inventory work does not distort the Chrome startup measurements.

## Highlights

- 5-second clean baseline with Chrome closed
- Manual Chrome launch only — no fragile browser automation
- 250 ms startup sampling to catch short CPU spikes
- System CPU, Chrome CPU, Chrome RAM, process count, available RAM, disk throughput
- Top CPU processes during the capture
- Privacy-reduced Chrome process snapshot — **no full command lines or URLs**
- Chrome extension inventory by profile
- Windows Defender status
- WHEA Event ID 17 collection for the last 24 hours
- PCI/PCIe device and driver inventory
- Local `Summary.txt`, CSV/JSON data, and ZIP package
- No telemetry, no cloud upload, no account required
- Standard Windows installer/uninstaller

## Supported systems

- Windows 10 x64
- Windows 11 x64
- Google Chrome desktop

The source code uses Python 3.11+ and `psutil`. End users do **not** need Python when using the packaged release.

## Install

### Recommended: GitHub Release installer

1. Open the repository's **Releases** page.
2. Download `Chrome-Diagnostic-Setup-vX.Y.Z.exe`.
3. Run the installer.
4. Start **Chrome Diagnostic** from the Start menu.

The installer is built by GitHub Actions from this public repository. Until the project has a code-signing certificate, Windows SmartScreen may show an "unknown publisher" warning. Verify the SHA-256 checksum published with each release.

### Run from source

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m chrome_diagnostic
```

## How to use

1. Close every Chrome window.
2. Click **Start diagnostic**.
3. Keep Chrome closed during the 5-second baseline.
4. When the application shows **OPEN CHROME NOW**, launch Chrome using the shortcut you normally use.
5. Continue using Chrome normally for the 60-second capture.
6. The application creates a ZIP under:

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
| `PCIe-Devices.json` | PCI/PCIe device/driver inventory |
| `report.json` | Machine-readable diagnostic summary and samples |

See [docs/REPORTS.md](docs/REPORTS.md) for details.

## Privacy

Chrome Diagnostic has **no telemetry** and does not upload reports anywhere. Reports remain on the local PC unless the user shares them.

To reduce accidental disclosure, the public release does **not** save full Chrome command lines or browsing URLs. Reports can still contain hardware IDs, profile labels, extension IDs, driver versions and Windows event details. Review a report before posting it publicly.

Read [PRIVACY.md](PRIVACY.md).

## WHEA / PCIe notes

WHEA Event ID 17 means Windows reported a **corrected** PCI Express hardware error. A corrected error does not automatically prove that hardware is failing, but repeated events are useful evidence for driver, power-management, controller, link, firmware or hardware troubleshooting.

Chrome Diagnostic does not change BIOS, drivers, power plans or PCIe settings. It is a read-only diagnostic collector.

## Build a Windows release locally

Install Python 3.11+ and Inno Setup 6, then run:

```powershell
.\tools\build.ps1
```

The output is placed in `dist/`.

## Development

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check src tests
```

Architecture and release process:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/RELEASE.md](docs/RELEASE.md)

## Security

Please do not publish sensitive diagnostics in a public issue. Use the process described in [SECURITY.md](SECURITY.md) for security reports.

## License

MIT — see [LICENSE](LICENSE).
