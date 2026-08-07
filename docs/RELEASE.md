# Release process

1. Update the version in:
   - `src/chrome_diagnostic/__init__.py`
   - `pyproject.toml`
   - `installer/ChromeDiagnostic.iss`
   - `CHANGELOG.md`
2. Merge changes into `main`.
3. Create an annotated tag:

```powershell
git tag -a v1.0.0 -m "Chrome Diagnostic v1.0.0"
git push origin v1.0.0
```

4. The GitHub `release.yml` workflow:
   - runs tests/lint,
   - builds the Windows EXE with PyInstaller,
   - builds the installer with Inno Setup,
   - generates SHA-256 checksums,
   - creates a GitHub Release and uploads artifacts.

5. Download the published installer on a clean Windows machine and perform a smoke test before marking a future release as stable.

## Code signing

The workflow does not sign binaries by default. If a code-signing certificate is added later, store credentials in GitHub Actions Secrets and add a signing step before Inno Setup packaging.
