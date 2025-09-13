# 🔎 OSV Vulnerability Bot — Always‑Green Python Project

Automated vulnerability scanning and CI hardening for Python projects.  
This repo integrates **OSV‑Scanner** against `poetry.lock`, a strict **green CI** (ruff, black, pytest, mypy), and **CodeQL** for security—all guarded by branch protection.

<div align="center">

[![CI](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/ci.yml)
[![CodeQL](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/github/v/release/CoderDeltaLAN/osv-vuln-bot?display_name=tag)](https://github.com/CoderDeltaLAN/osv-vuln-bot/releases)
![Python 3.11|3.12](https://img.shields.io/badge/Python-3.11%20|%203.12-3776AB?logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## What this project does

- Runs **OSV‑Scanner** on `poetry.lock` to surface known vulnerabilities early.
- Enforces **always‑green** PRs with required checks: *Analyze*, *python (3.11)*, *python (3.12)*.
- Uses **CodeQL** for code‑scanning and **Release Drafter** + conventional commits for clean releases.
- Keeps **linear history** via squash‑merge and branch protection.

---

## Quick start (local)

```bash
# Install tooling (inside your virtualenv)
python -m pip install -U pip
pip install ruff black pytest mypy

# Lint/format/tests/types (mirrors CI)
ruff check .
black --check .
PYTHONPATH=src pytest -q
mypy src
```

### Local OSV scan
```bash
# Option A: Using osv-scanner CLI
python -m pip install osv-scanner
osv-scanner --lockfile=poetry.lock

# Option B: Docker (if you prefer containers)
docker run --rm -v "$PWD:/work" ghcr.io/google/osv-scanner:latest \
  --lockfile=/work/poetry.lock
```

> CI runs these gates on PRs and `main`. Branch protection blocks merges if any fail.

---

## CI / CD

- **CI:** `.github/workflows/ci.yml` → Linux, Python 3.11/3.12, ruff/black/pytest/mypy.
- **Security:** `.github/workflows/codeql.yml` → CodeQL analysis on PRs and `main`.
- **Releases:** Drafted by Release Drafter; tags via GitHub Releases. Keep commits conventional for good notes.

Example Python steps (as in CI):

```yaml
- run: python -m pip install -U pip
- run: pip install ruff black pytest mypy
- run: ruff check .
- run: black --check .
- run: pytest -q
- run: mypy src
```

---

## Branch protection (main)

- Required checks: **Analyze**, **python (3.11)**, **python (3.12)**.
- Linear history, no force‑push, conversations resolved, admins enforced.
- Squash‑merge only; auto‑merge allowed once checks pass.

---

## Contributing

- Use **small, atomic PRs** and **Conventional Commits** (e.g., `feat: ...`, `fix: ...`, `docs: ...`).
- Keep local gates green before pushing.
- Enable **auto‑merge** when checks pass.

---

## Security Policy

Please report vulnerabilities via **GitHub Security Advisories** (private) or open a minimal reproducible issue if appropriate. CodeQL and OSV scans run automatically on PRs and `main`.

---

## Sponsorship

If this project is useful, consider supporting continued maintenance and polish. Thank you!  
[**PayPal Donate**](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE).

