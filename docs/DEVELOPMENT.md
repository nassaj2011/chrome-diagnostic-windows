# Development

## Requirements

- Windows 10/11 recommended for full functionality
- Python 3.11+

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Run

```powershell
python -m chrome_diagnostic
```

## Tests and lint

```powershell
python -m pytest -q
python -m ruff check src tests
```

## Build

Install Inno Setup 6, then:

```powershell
.\tools\build.ps1
```

The repository intentionally does not commit generated EXE/installer binaries. Release artifacts are produced by GitHub Actions from tags.
