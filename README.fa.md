# Chrome Diagnostic برای Windows

یک ابزار متن‌باز و حریم‌خصوصی‌محور برای بررسی **جهش CPU هنگام اجرای Chrome**، مصرف RAM، تعداد پردازش‌ها، افزونه‌ها و خطاهای اصلاح‌شده **WHEA / PCIe** در ویندوز.

> این پروژه مستقل است و وابستگی یا تأیید رسمی از سوی Google ندارد.

## چه مشکلی را حل می‌کند؟

گاهی با بازشدن Chrome سیستم برای چند ثانیه شدیداً کند می‌شود و CPU تا نزدیکی 100٪ می‌رود، اما تا Task Manager باز شود مصرف پایین آمده است. این برنامه همان بازه ابتدایی را با نمونه‌برداری سریع ثبت می‌کند و یک گزارش ZIP قابل تحلیل می‌سازد.

## قابلیت‌ها

- ثبت 5 ثانیه وضعیت پایه در حالی که Chrome بسته است
- اجرای Chrome توسط خود کاربر؛ بدون Auto-Launch شکننده
- نمونه‌برداری هر 250 میلی‌ثانیه برای ثبت جهش‌های کوتاه
- CPU کل سیستم و Chrome، RAM Chrome، تعداد Processها، RAM آزاد و I/O دیسک
- ثبت Processهای پرمصرف
- ثبت اطلاعات Processهای Chrome بدون ذخیره URL و Command Line کامل
- فهرست Extensionهای نصب‌شده بر اساس Profile
- وضعیت Microsoft Defender
- جمع‌آوری WHEA Event ID 17 مربوط به 24 ساعت گذشته
- فهرست PCI/PCIe و Driverها
- ساخت Summary، CSV، JSON و ZIP به‌صورت کاملاً Local
- بدون Telemetry و بدون ارسال خودکار اطلاعات
- Installer و Uninstaller استاندارد ویندوز

## روش استفاده

1. همه پنجره‌های Chrome را ببندید.
2. روی **Start diagnostic** بزنید.
3. در 5 ثانیه اول Chrome را بسته نگه دارید.
4. وقتی پیام **OPEN CHROME NOW** ظاهر شد، Chrome را از میانبر همیشگی خود باز کنید.
5. برنامه 60 ثانیه وضعیت را ثبت می‌کند.
6. گزارش داخل این مسیر ساخته می‌شود:

```text
Documents\Chrome Diagnostic Reports
```

## حریم خصوصی

برنامه هیچ Telemetry یا Upload خودکاری ندارد. گزارش‌ها روی سیستم باقی می‌مانند مگر اینکه خود کاربر آنها را به اشتراک بگذارد.

نسخه عمومی عمداً Full Command Line و URLهای Chrome را ذخیره نمی‌کند. با این حال گزارش می‌تواند شامل شناسه سخت‌افزار، نام Profile، شناسه Extension، نسخه Driver و اطلاعات Event Log باشد؛ قبل از انتشار عمومی گزارش آن را بررسی کنید.

جزئیات بیشتر: [PRIVACY.md](PRIVACY.md)

## نصب برای کاربران عادی

از بخش **Releases** فایل زیر را دانلود کنید:

```text
Chrome-Diagnostic-Setup-vX.Y.Z.exe
```

بعد از نصب، برنامه از Start Menu قابل اجرا و از **Settings > Apps > Installed apps** قابل حذف است.

تا زمانی که پروژه Code Signing Certificate نداشته باشد، ممکن است Windows SmartScreen هشدار Unknown Publisher نمایش دهد. SHA-256 هر Release منتشر می‌شود تا فایل قابل بررسی باشد.

## اجرای سورس برای توسعه‌دهندگان

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m chrome_diagnostic
```

## مجوز

MIT — فایل [LICENSE](LICENSE) را ببینید.
