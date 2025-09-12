from __future__ import annotations
import httpx
import osv_vuln_bot.osv_client as oc


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


def test_regex_uses_max_number_in_string():
    client = _mock_client_with_scores(["CVSS:3.1/.../8.8"])
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 1 and counts["high"] == 1


def test_non_numeric_scores_count_none():
    client = _mock_client_with_scores(["foo", ""])
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 2 and counts["none"] == 2


def test_close_client_branch(monkeypatch):
    # Fuerza ruta client=None y cierre interno
    client = _mock_client_with_scores(["9.0"])
    monkeypatch.setattr(oc, "create_http_client", lambda: client)
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=None)
    assert total == 1 and counts["critical"] == 1
