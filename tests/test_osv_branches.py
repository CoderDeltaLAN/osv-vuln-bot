from __future__ import annotations
import httpx
import osv_vuln_bot.osv_client as oc


def _mock(scores):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(oc.OSV_QUERYBATCH_URL):
            vulns = [
                {"id": f"V{i}", "severity": [{"type": "CVSS_V3", "score": s}]}
                for i, s in enumerate(scores)
            ]
            return httpx.Response(200, json={"results": [{"vulns": vulns}]})
        return httpx.Response(404, json={"error": "not found"})

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_numeric_int_and_bad_string_paths():
    # 5 -> moderate, "CVSS:" -> none
    client = _mock([5, "CVSS:"])
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 2 and counts["moderate"] == 1 and counts["none"] == 1


def test_results_none_and_item_without_vulns():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(oc.OSV_QUERYBATCH_URL):
            return httpx.Response(200, json={"results": [{}, {"vulns": []}]})
        return httpx.Response(404, json={"error": "not found"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    total, counts, results = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 0 and results and all(v == 0 for v in counts.values())
