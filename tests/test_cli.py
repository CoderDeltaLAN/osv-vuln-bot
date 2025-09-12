from __future__ import annotations

import json
from pathlib import Path

import httpx

import osv_vuln_bot.cli as cli
import osv_vuln_bot.osv_client as oc


def test_cli_scan_exit_codes(tmp_path: Path, monkeypatch):
    # Fake deps file
    deps = [
        {"ecosystem": "PyPI", "name": "requests", "version": "2.32.0"},
    ]
    deps_path = tmp_path / "deps.json"
    deps_path.write_text(json.dumps(deps), encoding="utf-8")

    # Fake OSV response: one HIGH vuln
    fake = {
        "results": [
            {"vulns": [{"id": "OSV-XYZ", "severity": [{"type": "CVSS_V3", "score": "7.5"}]}]}
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(oc.OSV_QUERYBATCH_URL):
            return httpx.Response(200, json=fake)
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    # Patch create_http_client to use our mock client
    monkeypatch.setattr(oc, "create_http_client", lambda: client)

    # Case 1: --fail-on critical => should not fail (only high present)
    code = cli.main(["--deps", str(deps_path), "--fail-on", "critical"])
    assert code == 0

    # Case 2: --fail-on high => should fail (high present)
    out_path = tmp_path / "report.json"
    code = cli.main(["--deps", str(deps_path), "--out", str(out_path), "--fail-on", "high"])
    assert code == 1
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["total"] == 1 and data["counts"]["high"] == 1
