from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: gen_deps_from_poetry.py <poetry.lock>", file=sys.stderr)
        return 2
    lock_path = Path(sys.argv[1])
    data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    pkgs = data.get("package") or []
    seen: set[tuple[str, str]] = set()
    out = []
    for p in pkgs:
        name = p.get("name")
        version = p.get("version")
        if not name or not version:
            continue
        key = (str(name), str(version))
        if key in seen:
            continue
        seen.add(key)
        out.append({"ecosystem": "PyPI", "name": key[0], "version": key[1]})
    json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
