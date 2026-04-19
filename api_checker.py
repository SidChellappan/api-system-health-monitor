"""api_checker.py - REST endpoint health check module."""

import time
from typing import Any

import requests


def check_api_endpoints(endpoints: list[dict]) -> list[dict[str, Any]]:
    """Poll each configured REST endpoint and return health results."""
    results = []
    for ep in endpoints:
        name = ep.get("name", ep["url"])
        url = ep["url"]
        method = ep.get("method", "GET").upper()
        expected_status = ep.get("expected_status", 200)
        timeout_ms = ep.get("timeout_ms", 3000)
        timeout_sec = timeout_ms / 1000.0

        result: dict[str, Any] = {"name": name, "url": url}
        try:
            start = time.monotonic()
            resp = requests.request(method, url, timeout=timeout_sec)
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            result["http_status"] = resp.status_code
            result["latency_ms"] = latency_ms
            if resp.status_code == expected_status:
                result["status"] = "ok"
            else:
                result["status"] = "warn"
                result["detail"] = f"Expected {expected_status}, got {resp.status_code}"
        except requests.exceptions.Timeout:
            result["status"] = "critical"
            result["detail"] = f"Timeout after {timeout_ms}ms"
        except requests.exceptions.ConnectionError as exc:
            result["status"] = "critical"
            result["detail"] = f"Connection error: {exc}"
        except Exception as exc:
            result["status"] = "critical"
            result["detail"] = str(exc)

        results.append(result)
    return results
