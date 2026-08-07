from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path
from collections.abc import Iterable, Mapping, Sequence

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def run_hidden(args: Sequence[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    kwargs: dict = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
        "check": False,
    }
    if os.name == "nt":
        kwargs["creationflags"] = CREATE_NO_WINDOW
    return subprocess.run(list(args), **kwargs)


def run_powershell(script: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    executable = "powershell.exe" if os.name == "nt" else "pwsh"
    return run_hidden(
        [executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
        timeout=timeout,
    )


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8-sig")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def mb(value: int | float) -> float:
    return round(float(value) / (1024 * 1024), 1)
