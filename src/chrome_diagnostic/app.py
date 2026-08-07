from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from . import __version__
from .chrome import chrome_is_running
from .collector import ChromeNotDetectedError, ChromeStillRunningError, run_diagnostic

APP_NAME = "Chrome Diagnostic"


def default_report_root() -> Path:
    documents = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents"
    return documents / "Chrome Diagnostic Reports"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} {__version__}")
        self.geometry("760x570")
        self.minsize(700, 520)
        self.cancel_event = threading.Event()
        self.events: queue.Queue[tuple] = queue.Queue()
        self.latest_zip: Path | None = None
        self.worker: threading.Thread | None = None
        self._build()
        self.after(100, self._poll_events)

    def _build(self) -> None:
        self.configure(padx=24, pady=22)
        ttk.Label(self, text="Chrome Diagnostic", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(
            self,
            text="Privacy-first Windows diagnostics for Chrome startup CPU spikes and WHEA/PCIe warnings",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 18))

        card = ttk.LabelFrame(self, text="Startup performance test", padding=18)
        card.pack(fill="x")
        self.instructions = ttk.Label(
            card,
            text=(
                "1. Close every Chrome window.\n"
                "2. Click Start diagnostic and keep Chrome closed during the 5-second baseline.\n"
                "3. When the app says ‘Open Chrome now’, launch Chrome from your normal shortcut.\n"
                "4. Chrome Diagnostic will capture 60 seconds and build a local ZIP report."
            ),
            justify="left",
        )
        self.instructions.pack(anchor="w")

        buttons = ttk.Frame(card)
        buttons.pack(fill="x", pady=(16, 0))
        self.start_btn = ttk.Button(buttons, text="Start diagnostic", command=self.start_test)
        self.start_btn.pack(side="left")
        self.cancel_btn = ttk.Button(buttons, text="Cancel", command=self.cancel_test, state="disabled")
        self.cancel_btn.pack(side="left", padx=8)
        ttk.Button(buttons, text="Open reports folder", command=self.open_reports).pack(side="right")

        self.progress = ttk.Progressbar(card, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(18, 6))
        self.status_label = ttk.Label(card, text="Ready")
        self.status_label.pack(anchor="w")

        self.open_chrome = tk.Label(
            card,
            text="OPEN CHROME NOW",
            bg="#fff3cd",
            fg="#664d03",
            font=("Segoe UI", 16, "bold"),
            padx=12,
            pady=12,
        )

        result = ttk.LabelFrame(self, text="Result", padding=18)
        result.pack(fill="x", pady=(16, 0))
        self.result_label = ttk.Label(result, text="No report created yet.", wraplength=670, justify="left")
        self.result_label.pack(anchor="w")
        self.open_report_btn = ttk.Button(result, text="Show latest ZIP", command=self.open_latest, state="disabled")
        self.open_report_btn.pack(anchor="w", pady=(10, 0))

        privacy = ttk.LabelFrame(self, text="Privacy", padding=14)
        privacy.pack(fill="x", pady=(16, 0))
        ttk.Label(
            privacy,
            text=(
                "No telemetry and no automatic upload. Reports stay on this PC. Full Chrome command lines and URLs are not stored. "
                "Reports may contain hardware identifiers, profile labels, extension IDs and Windows event details."
            ),
            wraplength=680,
            justify="left",
        ).pack(anchor="w")

    def start_test(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if chrome_is_running():
            messagebox.showwarning(
                APP_NAME,
                "Chrome is still running. Close all Chrome windows first.\n\nIf Chrome keeps background processes alive, exit Chrome from its system tray icon and try again.",
            )
            return
        self.cancel_event.clear()
        self.latest_zip = None
        self.progress["value"] = 1
        self.status_label.config(text="Starting diagnostic…")
        self.result_label.config(text="Diagnostic in progress…")
        self.open_report_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.open_chrome.pack_forget()
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def _worker(self) -> None:
        try:
            path = run_diagnostic(default_report_root(), self._status_from_worker, self.cancel_event)
            self.events.put(("success", path))
        except (ChromeStillRunningError, ChromeNotDetectedError) as exc:
            self.events.put(("error", str(exc)))
        except Exception as exc:  # top-level guard for a desktop utility
            self.events.put(("error", f"Diagnostic failed: {exc}"))

    def _status_from_worker(self, phase: str, fraction: float, message: str) -> None:
        self.events.put(("status", phase, fraction, message))

    def _poll_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "status":
                    _, phase, fraction, text = event
                    self.progress["value"] = max(0, min(100, float(fraction) * 100))
                    self.status_label.config(text=text)
                    if phase == "waiting":
                        if not self.open_chrome.winfo_ismapped():
                            self.open_chrome.pack(fill="x", pady=(12, 0))
                    else:
                        self.open_chrome.pack_forget()
                elif kind == "success":
                    self.latest_zip = Path(event[1])
                    self.progress["value"] = 100
                    self.status_label.config(text="Diagnostic complete")
                    self.result_label.config(text=f"Report created:\n{self.latest_zip}")
                    self.open_report_btn.config(state="normal")
                    self.start_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
                    self.open_chrome.pack_forget()
                elif kind == "error":
                    self.status_label.config(text="Diagnostic stopped")
                    self.result_label.config(text=event[1])
                    self.start_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
                    self.open_chrome.pack_forget()
                    messagebox.showerror(APP_NAME, event[1])
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def cancel_test(self) -> None:
        self.cancel_event.set()
        self.cancel_btn.config(state="disabled")
        self.status_label.config(text="Cancelling…")

    def open_reports(self) -> None:
        root = default_report_root()
        root.mkdir(parents=True, exist_ok=True)
        self._open_path(root)

    def open_latest(self) -> None:
        if self.latest_zip and self.latest_zip.exists():
            if os.name == "nt":
                subprocess.Popen(["explorer.exe", "/select,", str(self.latest_zip)])
            else:
                self._open_path(self.latest_zip.parent)

    @staticmethod
    def _open_path(path: Path) -> None:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
