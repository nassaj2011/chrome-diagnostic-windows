from pathlib import Path

from chrome_diagnostic import __version__


def test_version_is_consistent():
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    inno = (root / "installer" / "ChromeDiagnostic.iss").read_text(encoding="utf-8")
    assert f'version = "{__version__}"' in pyproject
    assert f'#define MyAppVersion "{__version__}"' in inno
