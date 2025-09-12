from __future__ import annotations
from pathlib import Path
import json
import httpx
import osv_vuln_bot.osv_client as oc
import osv_vuln_bot.cli as cli


def _mock_client_with_scores(scores):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(oc.OSV_QUERYBATCH_URL):
            vulns = [
                {"id": f"V{i}", "severity": [{"type": "CVSS_V3", "score": s}]}
                for i, s in enumerate(scores)
            ]
            return httpx.Response(200, json={"results": [{"vulns": vulns}]})
        return httpx.Response(404, json={"error": "not found"})

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_scan_packages_buckets_varios():
    client = _mock_client_with_scores(["0.0", "3.9", "4.0", "7.0", "9.0", "CVSS:3.1/.../8.8"])
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 6
    # 0.0 -> none, 3.9 -> low, 4.0 -> moderate, 7.0 -> high, 9.0 -> critical, 8.8 -> high
    assert counts["none"] == 1
    assert counts["low"] == 1
    assert counts["moderate"] == 1
    assert counts["high"] == 2
    assert counts["critical"] == 1


def test_scan_empty_returns_zeros():
    total, counts, results = oc.scan_packages([], client=_mock_client_with_scores([]))
    assert total == 0 and results == [] and all(v == 0 for v in counts.values())


def test_cli_subcommand_scan_exit(tmp_path: Path, monkeypatch):
    deps = [{"ecosystem": "PyPI", "name": "req", "version": "1.0.0"}]
    p = tmp_path / "deps.json"
    p.write_text(json.dumps(deps), encoding="utf-8")
    # Alta -> debe fallar con --fail-on low
    client = _mock_client_with_scores(["7.2"])
    monkeypatch.setattr(oc, "create_http_client", lambda: client)
    assert cli.main(["scan", "--deps", str(p), "--fail-on", "low"]) == 1
    # Solo none -> no debe fallar con --fail-on critical
    client2 = _mock_client_with_scores(["0.0"])
    monkeypatch.setattr(oc, "create_http_client", lambda: client2)
    assert cli.main(["--deps", str(p), "--fail-on", "critical"]) == 0
