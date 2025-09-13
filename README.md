# ⭐ osv-vuln-bot — Always-Green OSV Scanner (Python CLI)

A lean, production-grade **Python CLI** to audit dependencies against [OSV.dev](https://osv.dev/).  
It mirrors CI locally, enables **CodeQL**, enforces a **strict always-green** workflow (linear history + required checks), and fails builds when risk thresholds are met.

<div align="center">

[![CI / build](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/build.yml)
[![CodeQL Analysis](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/osv-vuln-bot/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/github/v/release/CoderDeltaLAN/osv-vuln-bot?display_name=tag)](https://github.com/CoderDeltaLAN/osv-vuln-bot/releases)
![Python 3.11|3.12](https://img.shields.io/badge/Python-3.11%20|%203.12-3776AB?logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Donate](https://img.shields.io/badge/Donate-PayPal-0070ba?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)

</div>

---

## Repo layout

```text
.
├── scripts/                      # Utilities (e.g., gen_deps_from_poetry.py)
├── examples/deps.sample.json     # Example dependency inventory
├── src/osv_vuln_bot/             # Python package + CLI
├── tests/                        # pytest (95%+ coverage)
└── .github/workflows/            # build.yml, codeql.yml, etc.
```

---

## 🚀 Quick Start (Python)

```bash
cd /home/user/Proyectos/osv-vuln-bot
poetry install --no-interaction

# Local gates (mirror CI)
poetry run ruff check .
poetry run black --check .
PYTHONPATH=src poetry run pytest -q
poetry run mypy src
```

### CLI usage

Generate inventory from `poetry.lock` and scan:

```bash
cd /home/user/Proyectos/osv-vuln-bot
poetry run python scripts/gen_deps_from_poetry.py poetry.lock > deps.json
poetry run osv-vuln-bot --deps deps.json --fail-on high
```

Help & options:

```bash
cd /home/user/Proyectos/osv-vuln-bot
poetry run osv-vuln-bot --help
```

**Notes**  
- `--deps` expects a JSON array of `{ "ecosystem":"PyPI", "name":"<pkg>", "version":"<ver>" }`.  
- `--fail-on` supports: `none | low | moderate | high | critical`.  
- If the threshold is met or exceeded, the process **exits non-zero** (perfect for CI gating).

---

## 🧪 Local Developer Workflow (mirrors CI)

```bash
cd /home/user/Proyectos/osv-vuln-bot
poetry run ruff check .
poetry run black --check .
PYTHONPATH=src poetry run pytest -q
poetry run mypy src
```

---

## 🔧 CI (GitHub Actions)

- Linux matrix **Python 3.11 / 3.12** with steps matching local gates.
- **OSV scan** integrated (job fails when the risk threshold is hit).
- **Artifacts** with per-job logs for troubleshooting.
- **CodeQL** runs on PRs and `main`.

Relevant Python job fragment:

```yaml
- run: python -m pip install --upgrade pip
- run: pip install poetry
- run: poetry install --no-interaction
- run: poetry run ruff check .
- run: poetry run black --check .
- env:
    PYTHONPATH: src
  run: poetry run pytest -q
- run: poetry run mypy src
- name: Generate deps from poetry.lock
  run: poetry run python scripts/gen_deps_from_poetry.py poetry.lock > deps.ci.json
- name: OSV scan (fail on high)
  run: poetry run osv-vuln-bot --deps deps.ci.json --fail-on high
```

---

## 🗺 When to Use This Project

- You need **security gating** with OSV on PRs and `main`.
- Python repos that must **stay green** (branch protections + auto-merge).
- Prefer **linear history** via squash-merge.

---

## 🧩 Customization

- Tune `--fail-on` to match your risk appetite.  
- Swap the inventory source (e.g., generate JSON from `requirements.txt`).  
- Extend the CI matrix or add OS runners if required.

---

## 🛡 Security

- Private disclosures via GitHub Security Advisories.  
- **CodeQL** enabled; OSV runs on every PR and `main`.  
- Secret scanning is enabled; never commit secrets.

---

## 🙌 Contributing

- **Small, atomic PRs** using Conventional Commits.  
- Keep **local gates** green before pushing.  
- Enable **auto-merge** once checks pass.

---

## 📈 SEO Keywords

osv scanner python cli, osv.dev vulnerability audit, poetry lock deps to osv,  
always green ci python, ruff black pytest mypy, github actions matrix, codeql analysis,  
branch protection required checks, squash merge linear history, dependency security gating

---

## 👤 Author

**CoderDeltaLAN (Yosvel)**  
Email: `coderdeltalan.cargo784@8alias.com`  
GitHub: https://github.com/CoderDeltaLAN

---

## 💚 Donations & Sponsorship

If this project saves you time, consider supporting ongoing maintenance. Thank you!
[![Donate](https://img.shields.io/badge/Donate-PayPal-0070ba?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)

---

## 📄 License

Released under the **MIT License**. See [LICENSE](LICENSE).
