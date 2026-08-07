# Chrome Diagnostic برای Windows

[![CI](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/ci.yml)
[![Windows Build](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/build.yml/badge.svg)](https://github.com/nassaj2011/chrome-diagnostic-windows/actions/workflows/build.yml)
[![Latest Release](https://img.shields.io/github/v/release/nassaj2011/chrome-diagnostic-windows?display_name=tag)](https://github.com/nassaj2011/chrome-diagnostic-windows/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

یک ابزار متن‌باز و حریم‌خصوصی‌محور برای Windows که برای بررسی **جهش CPU هنگام اجرای Chrome**، رشد مصرف RAM، افزایش تعداد Processها، فشار Extensionها و خطاهای اصلاح‌شده **WHEA / PCIe** ساخته شده است.

> این پروژه مستقل است و وابستگی یا تأیید رسمی از سوی Google ندارد. فایل [NOTICE.md](NOTICE.md) را ببینید.

[English README](README.md)

## دانلود

برای بیشتر کاربران، روش پیشنهادی استفاده از Installer رسمی موجود در آخرین GitHub Release است:

**[دریافت آخرین Release](https://github.com/nassaj2011/chrome-diagnostic-windows/releases/latest)**

فایل‌های Release شامل این موارد هستند:

- `Chrome-Diagnostic-Setup-vX.Y.Z.exe` — Installer و Uninstaller استاندارد Windows
- `ChromeDiagnostic.exe` — نسخه Portable
- `SHA256SUMS.txt` — Checksum برای بررسی صحت فایل‌های Release

> تا زمانی که پروژه Code Signing Certificate نداشته باشد، ممکن است Windows SmartScreen هشدار **Unknown publisher** نشان دهد. SmartScreen یا Microsoft Defender را خاموش نکنید؛ در صورت نیاز SHA-256 فایل را بررسی کنید.

## چه مشکلی را حل می‌کند؟

گاهی با بازشدن Chrome سیستم برای چند ثانیه شدیداً کند می‌شود و CPU تا نزدیکی 100٪ می‌رود، اما تا Task Manager باز شود مصرف پایین آمده است.

Chrome Diagnostic همان بازه ابتدایی را با نمونه‌برداری سریع ثبت می‌کند و یک گزارش ZIP محلی و قابل تحلیل می‌سازد.

این ابزار می‌تواند به تفکیک چند سناریوی رایج کمک کند:

- جهش CPU خود Chrome یا Rendererها
- فشار Extensionها هنگام Startup
- رشد مصرف RAM یا تعداد Processها
- رقابت Process دیگری در Windows با Chrome
- فعالیت Storage هنگام Startup
- خطاهای WHEA / PCIe که ممکن است یک مشکل مستقل مربوط به Driver، Power Management، Firmware، Controller، Link یا Hardware باشند

Chrome Diagnostic یک ابزار **فقط-خواندنی (Read-only)** است و تنظیمات Chrome، Driverها، BIOS، Power Plan یا تنظیمات PCIe را تغییر نمی‌دهد.

## قابلیت‌ها

- ثبت 5 ثانیه وضعیت پایه در حالی که Chrome بسته است
- اجرای Chrome توسط خود کاربر؛ بدون Auto-Launch شکننده
- نمونه‌برداری هر 250 میلی‌ثانیه برای ثبت جهش‌های کوتاه
- CPU کل سیستم و Chrome، RAM Chrome، تعداد Processها، RAM آزاد و Disk Throughput
- ثبت Processهای پرمصرف
- ثبت اطلاعات Processهای Chrome بدون ذخیره URL و Full Command Line
- فهرست Extensionهای نصب‌شده بر اساس Profile
- وضعیت Microsoft Defender
- جمع‌آوری WHEA Event ID 17 مربوط به 24 ساعت گذشته
- فهرست PCI/PCIe و Driverها
- ساخت Summary، CSV، JSON و ZIP به‌صورت Local
- بدون Telemetry، Upload یا Account
- Installer و Uninstaller استاندارد Windows
- نسخه Portable در هر Release

## سیستم‌های پشتیبانی‌شده

- Windows 10 x64
- Windows 11 x64
- Google Chrome Desktop

سورس پروژه از Python 3.11+ و `psutil` استفاده می‌کند، اما کاربران نسخه Release به Python نیاز ندارند.

## شروع سریع

1. آخرین نسخه Chrome Diagnostic را از GitHub Release نصب کنید.
2. همه پنجره‌های Chrome را ببندید.
3. Chrome Diagnostic را اجرا کنید.
4. روی **Start diagnostic** بزنید.
5. در 5 ثانیه Baseline، Chrome را بسته نگه دارید.
6. با نمایش **OPEN CHROME NOW**، Chrome را از Shortcut همیشگی خود باز کنید.
7. در طول تست 60 ثانیه‌ای به‌صورت عادی از Chrome استفاده کنید.
8. گزارش در مسیر زیر ساخته می‌شود:

```text
Documents\Chrome Diagnostic Reports
```

## فایل‌های گزارش

| فایل | کاربرد |
|---|---|
| `Summary.txt` | جمع‌بندی خوانا و اندازه‌گیری‌های مهم |
| `Performance-Samples.csv` | Timeline نمونه‌برداری سریع Startup |
| `Top-Processes.csv` | Processهای پرمصرف در طول تست |
| `Chrome-Processes.csv` | اطلاعات کاهش‌یافته Processهای Chrome با رعایت حریم خصوصی |
| `Chrome-Extensions.csv` | Extensionهای نصب‌شده بر اساس Profile |
| `System-Info.json` | اطلاعات OS، CPU، Storage، GPU و Power Plan |
| `Defender-Status.json` | وضعیت Microsoft Defender |
| `WHEA-Events.json` | WHEA Event ID 17های اخیر |
| `PCIe-Devices.json` | Device و Driverهای PCI/PCIe |
| `report.json` | گزارش Machine-readable و Sampleها |

جزئیات بیشتر در [docs/REPORTS.md](docs/REPORTS.md).

## حریم خصوصی

Chrome Diagnostic **هیچ Telemetry یا Upload خودکاری ندارد**. گزارش‌ها روی سیستم باقی می‌مانند مگر اینکه خود کاربر آنها را به اشتراک بگذارد.

نسخه عمومی عمداً Full Command Line و URLهای Chrome را ذخیره نمی‌کند. با این حال گزارش ممکن است شامل Hardware ID، نام Profile، Extension ID، نسخه Driver و اطلاعات Windows Event باشد.

**قبل از انتشار عمومی یک Report، محتوای آن را بررسی کنید.**

جزئیات: [PRIVACY.md](PRIVACY.md)

## نکات WHEA / PCIe

WHEA Event ID 17 یعنی Windows یک **خطای اصلاح‌شده PCI Express** ثبت کرده است.

وجود یک Corrected Error به‌تنهایی اثبات نمی‌کند که Hardware در حال خرابی است، اما تکرار آن می‌تواند هنگام بررسی موارد زیر مفید باشد:

- پایداری PCIe Link
- Driver کنترلر یا Device
- Power Management
- Chipset / Platform Driver
- BIOS / Firmware
- Deviceهای متصل
- ایراد Hardware

Chrome Diagnostic این اطلاعات را فقط ثبت می‌کند و تغییری در سیستم ایجاد نمی‌کند.

## محدودیت‌های فعلی

- تمرکز فعلی برنامه روی Google Chrome در Windows است.
- برنامه ابزار تشخیصی است، نه ابزار Repair خودکار.
- فهرست Extensionها نشان می‌دهد چه Extensionهایی نصب هستند؛ اثر واقعی آنها باید با A/B Test بررسی شود.
- نسبت‌دادن فعالیت‌های بسیار کوتاه همیشه محدودیت ذاتی دارد، هرچند Sampler با فاصله 250ms برای ثبت Spikeهای کوتاه طراحی شده است.
- WHEA ممکن است کاملاً مستقل از Chrome باشد و فقط در صورت وجود همبستگی زمانی و تست کنترل‌شده باید به Chrome نسبت داده شود.
- فایل‌های Release فعلاً Code-signed نیستند.

## اجرای سورس

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m chrome_diagnostic
```

## ساخت Release در Windows

Python 3.11+ و Inno Setup 6 را نصب کنید و اجرا کنید:

```powershell
.\tools\build.ps1
```

خروجی داخل `dist/` ساخته می‌شود.

## توسعه

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check src tests
```

مستندات پروژه:

- [معماری](docs/ARCHITECTURE.md)
- [توسعه](docs/DEVELOPMENT.md)
- [ساختار گزارش](docs/REPORTS.md)
- [فرآیند Release](docs/RELEASE.md)
- [راهنمای مشارکت](CONTRIBUTING.md)

## امنیت

گزارش‌های حساس را در Issue عمومی منتشر نکنید. برای گزارش مسائل امنیتی از فرآیند توضیح‌داده‌شده در [SECURITY.md](SECURITY.md) استفاده کنید.

## مشارکت

Issue و Pull Request پذیرفته می‌شود. پیش از تغییرات عمده، [CONTRIBUTING.md](CONTRIBUTING.md) را مطالعه کنید.

## مجوز

MIT — فایل [LICENSE](LICENSE) را ببینید.
