# Contributing

Contributions are welcome.

## Before opening a pull request

1. Create a focused branch from `main`.
2. Keep diagnostics read-only unless a separate proposal explicitly justifies a mutation feature.
3. Avoid adding telemetry, automatic uploads or silent network calls.
4. Do not add collection of browsing history, cookies, passwords or full Chrome URLs.
5. Add or update tests for logic changes.
6. Run:

```powershell
python -m pytest -q
python -m ruff check src tests
```

## Pull requests

Describe:

- the problem being solved,
- the behavior before and after,
- Windows/Chrome versions tested,
- privacy impact,
- any new report fields.

## Diagnostic samples

Use synthetic or sanitized samples. Do not commit a user's real diagnostic ZIP to the repository.
