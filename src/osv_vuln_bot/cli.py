from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List

from . import osv_client as oc

ORDER: List[str] = ["none", "low", "moderate", "high", "critical"]


@dataclass(frozen=True)
class Args:
    deps: str
    out: str | None
    fail_on: str


def _normalize_argv(argv: List[str]) -> List[str]:
    # Aceptar subcomando opcional "scan"
    if argv and argv[0] == "scan":
        return argv[1:]
    return argv


def _parse_args(argv: List[str]) -> Args:
    argv = _normalize_argv(argv)
    p = argparse.ArgumentParser(prog="osv-vuln-bot", description="OSV vulnerability scanner")
    p.add_argument(
        "--deps", required=True, help="Path to deps.json (array of {ecosystem,name,version})"
    )
    p.add_argument("--out", required=False, help="Optional path to write a JSON report")
    p.add_argument(
        "--fail-on",
        required=False,
        default="none",
        choices=ORDER,
        help="Exit non-zero if >= level found",
    )
    ns = p.parse_args(argv)
    return Args(deps=ns.deps, out=ns.out, fail_on=ns.fail_on)


def _thresholds(level: str) -> List[str]:
    return ORDER[ORDER.index(level) :] if level in ORDER else ORDER


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])

    with open(args.deps, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    packages = [oc.Package(**item) for item in raw]

    client = oc.create_http_client()
    total, counts, results = oc.scan_packages(packages, client=client)

    report: Dict[str, Any] = {"total": int(total), "counts": counts, "results": results}
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    # Resumen corto
    print(f"found={total} counts={counts}")  # pragma: no cover

    # Exit status
    threshold = _thresholds(args.fail_on)
    should_fail = any((k != "none") and int(counts.get(k, 0)) > 0 for k in threshold)
    return 1 if should_fail else 0


def entrypoint() -> None:  # pragma: no cover
    sys.exit(main())
