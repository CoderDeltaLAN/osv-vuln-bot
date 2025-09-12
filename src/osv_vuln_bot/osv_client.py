from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Mapping
import httpx
import re

OSV_QUERYBATCH_URL = "https://api.osv.dev/v1/querybatch"

SeverityCounts = Dict[str, int]


@dataclass(frozen=True)
class Package:
    ecosystem: str
    name: str
    version: str


def build_querybatch(packages: List[Package]) -> Dict[str, Any]:
    return {
        "queries": [
            {"package": {"ecosystem": p.ecosystem, "name": p.name}, "version": p.version}
            for p in packages
        ]
    }


def create_http_client() -> httpx.Client:  # pragma: no cover
    return httpx.Client(timeout=httpx.Timeout(15.0, connect=10.0))


def _cvss_to_bucket(score: float) -> str:
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "moderate"
    if score > 0:
        return "low"
    return "none"


_NUM_RE = re.compile(r"(\d+(?:\.\d+)?)")


def _extract_cvss(sev_entry: Mapping[str, Any]) -> float:
    s = sev_entry.get("score")
    if isinstance(s, (int, float)):
        try:
            return float(s)
        except Exception:
            return 0.0
    if isinstance(s, str):
        try:
            return float(s)
        except Exception:
            nums = [float(m) for m in _NUM_RE.findall(s) if m]
            return max(nums) if nums else 0.0
    return 0.0


def _vuln_bucket(v: Dict[str, Any]) -> str:
    sev_list = v.get("severity") or []
    best = 0.0
    for s in sev_list:
        try:
            sc = _extract_cvss(s)
            if sc > best:
                best = sc
        except Exception:
            continue
    return _cvss_to_bucket(best)


def scan_packages(
    packages: List[Package], client: httpx.Client | None = None
) -> Tuple[int, SeverityCounts, List[Dict[str, Any]]]:
    if not packages:
        return 0, {"none": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}, []

    payload = build_querybatch(packages)
    close_client = False
    if client is None:
        client = create_http_client()
        close_client = True
    try:
        resp = client.post(OSV_QUERYBATCH_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
    finally:
        if close_client:
            client.close()

    results = data.get("results", []) or []
    counts: SeverityCounts = {"none": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
    total = 0
    for item in results:
        for v in item.get("vulns") or []:
            bucket = _vuln_bucket(v)
            counts[bucket] = int(counts.get(bucket, 0)) + 1
            total += 1
    return total, counts, results
