# osv-vuln-bot

Automated OSV vulnerability scanner CLI. Scans a dependency manifest and reports findings.
Roadmap: open dependency bump PRs prioritized by severity.

## Quick start
```bash
poetry install --no-interaction
poetry run osv-vuln-bot scan --deps examples/deps.sample.json --out /tmp/osv-report.json --fail-on high
```

## Manifest format
`deps.json` is an array of objects:
```json
[
  {"ecosystem":"PyPI","name":"requests","version":"2.32.0"},
  {"ecosystem":"npm","name":"lodash","version":"4.17.21"}
]
```

## CI
- Workflow: **CI / build** (Python 3.11/3.12; uploads logs artifacts).
- Code scanning: **CodeQL Analysis**.

License: MIT.
