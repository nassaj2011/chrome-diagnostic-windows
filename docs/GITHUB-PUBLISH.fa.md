# راهنمای انتشار Repository در GitHub

نام پیشنهادی Repository:

```text
chrome-diagnostic-windows
```

Description پیشنهادی:

```text
Privacy-first Windows tool for diagnosing Chrome startup CPU spikes, extensions, and WHEA/PCIe warnings.
```

Topics پیشنهادی:

```text
windows chrome diagnostics cpu performance whea pcie python tkinter psutil open-source
```

## 1. ساخت Repository در GitHub

در GitHub روی **New repository** بزنید و:

- Repository name: `chrome-diagnostic-windows`
- Visibility: `Public`
- Add a README: خاموش
- Add .gitignore: خاموش
- Choose a license: None

Repository باید خالی ساخته شود چون README، `.gitignore` و MIT License از قبل داخل پروژه هستند.

## 2. Push کردن سورس

ZIP آماده پروژه را Extract کنید؛ برای مثال:

```text
H:\Projects\chrome-diagnostic-windows
```

PowerShell را در همان پوشه باز کنید:

```powershell
cd H:\Projects\chrome-diagnostic-windows

git init -b main
git add .
git status
git commit -m "Initial public release v1.0.0"

git remote add origin https://github.com/YOUR_USERNAME/chrome-diagnostic-windows.git
git push -u origin main
```

`YOUR_USERNAME` را با Username واقعی GitHub جایگزین کنید.

اگر GitHub برای احراز هویت درخواست کرد، GitHub Desktop یا `gh auth login` روش‌های مناسب‌تری از Password هستند.

## 3. بررسی CI

بعد از Push وارد تب **Actions** شوید. دو Workflow باید دیده شوند:

- `CI`
- `Build Windows artifact`

`CI` تست‌ها و lint را اجرا می‌کند. Workflow دوم روی Windows یک EXE و Installer واقعی می‌سازد و آنها را به‌صورت Artifact نگه می‌دارد.

## 4. ساخت Release رسمی v1.0.0

وقتی Actions سبز شد:

```powershell
git tag -a v1.0.0 -m "Chrome Diagnostic v1.0.0"
git push origin v1.0.0
```

Push شدن Tag باعث اجرای Workflow `Release` می‌شود. این Workflow:

- تست‌ها را اجرا می‌کند؛
- EXE را با PyInstaller می‌سازد؛
- Installer را با Inno Setup می‌سازد؛
- SHA-256 می‌سازد؛
- GitHub Release ایجاد می‌کند؛
- فایل‌ها را روی Release قرار می‌دهد.

خروجی مورد انتظار:

```text
ChromeDiagnostic.exe
Chrome-Diagnostic-Setup-v1.0.0.exe
SHA256SUMS.txt
```

## 5. تنظیمات پیشنهادی Repository

در صفحه اصلی Repository بخش About:

- Description را وارد کنید.
- Topics پیشنهادی را اضافه کنید.
- Releases را فعال نگه دارید.

در **Settings > General**:

- Issues: On
- Discussions: اختیاری ولی برای پروژه عمومی مفید
- Wiki: در این پروژه ضروری نیست چون `docs/` داریم

در بخش Security:

- Dependabot alerts: On
- Secret scanning: در صورت در دسترس بودن On
- Private vulnerability reporting: On

پس از تثبیت اولین Release برای Branch `main` یک Branch protection rule تعریف کنید و حداقل CI موفق را برای Merge الزامی کنید.

## 6. SmartScreen و Code Signing

نسخه اول Code Signing Certificate ندارد. بنابراین Windows ممکن است برای Installer پیام **Unknown publisher** یا SmartScreen نمایش دهد. این موضوع در پروژه‌های Open Source جدید عادی است.

برای اعتماد بیشتر:

- Build را فقط در GitHub Actions انجام دهید؛
- SHA-256 را با Release منتشر کنید؛
- سورس Tag همان Release را حفظ کنید؛
- به کاربران توصیه نکنید SmartScreen یا Defender را غیرفعال کنند؛
- در آینده در صورت رشد پروژه Code Signing اضافه کنید.

## 7. قبل از Public کردن گسترده

روی یک Windows 10 و ترجیحاً Windows 11 این موارد Smoke Test شوند:

- Install
- Start diagnostic
- تشخیص بسته‌بودن Chrome
- Baseline 5 ثانیه‌ای
- پیام OPEN CHROME NOW
- تشخیص Chrome بعد از اجرای دستی
- Capture کامل 60 ثانیه
- ساخته‌شدن ZIP
- Open reports folder
- Uninstall از Settings > Apps

هیچ گزارش واقعی کاربر را داخل Repository Commit نکنید.
