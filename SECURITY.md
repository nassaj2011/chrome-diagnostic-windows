# Security policy

## Supported versions

Security fixes are provided for the latest released major/minor version.

## Reporting a vulnerability

Do not include sensitive diagnostic ZIP files in a public GitHub issue.

Preferred process:

1. Open the repository's **Security** tab.
2. Choose **Report a vulnerability** / **Private vulnerability reporting** if enabled.
3. Include the affected version, Windows version, reproduction steps and the minimum logs required.

If private vulnerability reporting is not enabled, open a public issue containing no secrets or diagnostic attachments and ask the maintainers for a private contact channel.

## Security design

- No telemetry or server component
- No browser automation
- No driver/BIOS/registry modification
- No administrator requirement for normal operation
- Full Chrome command lines and URLs are excluded from generated reports
- Windows diagnostic commands run non-interactively with hidden console windows
