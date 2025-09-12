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


def test_float_and_numeric_string_and_numbers_in_string():
    client = _mock([7.5, "9.1", "foo 2.0 bar", {"bad": "dict"}])
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    # 7.5 -> high, "9.1" -> critical, "foo 2.0 bar" -> low, dict -> none
    assert total == 4
    assert counts["high"] == 1
    assert counts["critical"] == 1
    assert counts["low"] == 1
    assert counts["none"] == 1


def test_empty_severity_bucket_none():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == httpx.URL(oc.OSV_QUERYBATCH_URL):
            return httpx.Response(
                200, json={"results": [{"vulns": [{"id": "V0", "severity": []}]}]}
            )
        return httpx.Response(404, json={"error": "not found"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    total, counts, _ = oc.scan_packages([oc.Package("PyPI", "x", "1")], client=client)
    assert total == 1 and counts["none"] == 1
