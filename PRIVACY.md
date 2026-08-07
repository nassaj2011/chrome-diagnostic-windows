# Privacy policy for the open-source application

Chrome Diagnostic is designed to operate locally.

## What the application does not do

- No telemetry
- No analytics SDK
- No advertising SDK
- No automatic report upload
- No browsing-history collection
- No saved full Chrome command lines
- No saved Chrome URLs
- No account or sign-in

## Information written to a local report

A diagnostic report can contain:

- Windows, CPU, RAM, storage and GPU information
- Chrome version and process metadata
- Chrome profile labels such as `Default` or `Profile 2`
- Installed Chrome extension IDs and manifest names/versions
- Process names, process IDs and memory/CPU measurements
- Microsoft Defender status
- WHEA Event ID 17 details
- PCI/PCIe hardware identifiers, driver names and versions

## Sharing reports

Reports are created under the user's Documents folder and are not transmitted by the application. If a user shares a ZIP in a GitHub issue, forum, email or chat, the recipient will receive the diagnostic metadata above.

Review reports before public posting. For security issues, use the private reporting path described in `SECURITY.md`.
