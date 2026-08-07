from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil


@dataclass(slots=True)
class ChromeProcessInfo:
    pid: int
    parent_pid: int | None
    process_type: str
    profile_directory: str
    is_extension_process: bool
    working_set_mb: float
    created_at: str


@dataclass(slots=True)
class ExtensionInfo:
    profile: str
    extension_id: str
    name: str
    version: str
    manifest_version: str


def find_chrome_executable() -> Path | None:
    if os.name != "nt":
        return None
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def chrome_processes() -> list[psutil.Process]:
    processes: list[psutil.Process] = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if (proc.info.get("name") or "").lower() == "chrome.exe":
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def chrome_is_running() -> bool:
    return bool(chrome_processes())


def _extract_flag(command_line: list[str], prefix: str) -> str:
    for item in command_line:
        if item.startswith(prefix):
            return item.split("=", 1)[1].strip('"') if "=" in item else ""
    return ""


def _process_type(command_line: list[str]) -> str:
    value = _extract_flag(command_line, "--type=")
    return value or "browser"


def snapshot_chrome_processes() -> list[ChromeProcessInfo]:
    """Return privacy-reduced process metadata. URLs and full command lines are never stored."""
    rows: list[ChromeProcessInfo] = []
    for proc in chrome_processes():
        try:
            cmd = proc.cmdline()
            created = proc.create_time()
            rows.append(
                ChromeProcessInfo(
                    pid=proc.pid,
                    parent_pid=proc.ppid(),
                    process_type=_process_type(cmd),
                    profile_directory=_extract_flag(cmd, "--profile-directory="),
                    is_extension_process="--extension-process" in cmd,
                    working_set_mb=round(proc.memory_info().rss / (1024 * 1024), 1),
                    created_at=__import__("datetime").datetime.fromtimestamp(created).astimezone().isoformat(timespec="seconds"),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return rows


def chrome_user_data_dir() -> Path | None:
    if os.name != "nt":
        return None
    root = Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data"
    return root if root.is_dir() else None


def _manifest_name(manifest: dict, extension_dir: Path) -> str:
    name = str(manifest.get("name") or "")
    if not name.startswith("__MSG_"):
        return name
    key = name[6:-2] if name.endswith("__") else name.replace("__MSG_", "").strip("_")
    locale = manifest.get("default_locale")
    locales = [locale, "en", "en_US"] if locale else ["en", "en_US"]
    for item in locales:
        if not item:
            continue
        messages = extension_dir / "_locales" / item / "messages.json"
        try:
            data = json.loads(messages.read_text(encoding="utf-8"))
            message = data.get(key, {}).get("message")
            if message:
                return str(message)
        except (OSError, json.JSONDecodeError):
            pass
    return name


def scan_extensions() -> list[ExtensionInfo]:
    root = chrome_user_data_dir()
    if root is None:
        return []
    rows: list[ExtensionInfo] = []
    profiles = [p for p in root.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile "))]
    for profile in profiles:
        ext_root = profile / "Extensions"
        if not ext_root.is_dir():
            continue
        for extension_dir in ext_root.iterdir():
            if not extension_dir.is_dir() or not re.fullmatch(r"[a-p]{32}", extension_dir.name):
                continue
            versions = sorted((p for p in extension_dir.iterdir() if p.is_dir()), reverse=True)
            if not versions:
                continue
            version_dir = versions[0]
            manifest_path = version_dir / "manifest.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                manifest = {}
            rows.append(
                ExtensionInfo(
                    profile=profile.name,
                    extension_id=extension_dir.name,
                    name=_manifest_name(manifest, version_dir),
                    version=str(manifest.get("version") or version_dir.name),
                    manifest_version=str(manifest.get("manifest_version") or ""),
                )
            )
    return rows


def dataclass_rows(values: list[object]) -> list[dict]:
    return [asdict(item) for item in values]
