from __future__ import annotations


import httpx

from osv_vuln_bot.osv_client import Package, build_querybatch, scan_packages, OSV_QUERYBATCH_URL


def test_build_querybatch():
    pkgs = [Package("PyPI", "requests", "2.32.0"), Package("npm", "lodash", "4.17.21")]
    q = build_querybatch(pkgs)
    assert "queries" in q and len(q["queries"]) == 2
    assert q["queries"][0]["package"]["ecosystem"] == "PyPI"


def test_scan_packages_with_mock_transport():
    # Prepare a fake OSV response with one HIGH vuln (CVSS 7.5)
    fake = {
        "results": [
            {"vulns": [{"id": "OSV-XYZ", "severity": [{"type": "CVSS_V3", "score": "7.5"}]}]}
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(OSV_QUERYBATCH_URL):
            return httpx.Response(200, json=fake)
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    total, counts, results = scan_packages([Package("PyPI", "requests", "2.32.0")], client=client)
    assert total == 1
    assert counts["high"] == 1
    assert results and results[0]["vulns"][0]["id"] == "OSV-XYZ"
