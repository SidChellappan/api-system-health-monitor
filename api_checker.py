"""REST endpoint health checking and response validation."""

from __future__ import annotations

import time
from typing import Any

import requests
from jsonschema import ValidationError, validate


STATUS_ORDER = {"ok": 0, "warn": 1, "critical": 2}


def _upgrade_status(current: str, candidate: str) -> str:
    return candidate if STATUS_ORDER[candidate] > STATUS_ORDER[current] else current


def _append_detail(result: dict[str, Any], message: str) -> None:
    existing = result.get("detail")
    result["detail"] = f"{existing} | {message}" if existing else message


def _validate_response_content(result: dict[str, Any], endpoint: dict[str, Any], response: requests.Response) -> None:
    expected_json_keys = endpoint.get("expected_json_keys", [])
    expected_json_schema = endpoint.get("expected_json_schema")
    expected_substring = endpoint.get("expected_substring")

    if expected_substring and expected_substring not in response.text:
        result["status"] = _upgrade_status(result["status"], "warn")
        _append_detail(result, f"Response missing expected substring '{expected_substring}'.")

    if not expected_json_keys and not expected_json_schema:
        return

    try:
        payload = response.json()
    except ValueError:
        result["status"] = _upgrade_status(result["status"], "warn")
        _append_detail(result, "Response body was not valid JSON.")
        return

    if expected_json_keys:
        missing_keys = [key for key in expected_json_keys if key not in payload]
        if missing_keys:
            result["status"] = _upgrade_status(result["status"], "warn")
            _append_detail(result, f"Missing expected JSON keys: {', '.join(missing_keys)}.")

    if expected_json_schema:
        try:
            validate(instance=payload, schema=expected_json_schema)
        except ValidationError as exc:
            result["status"] = _upgrade_status(result["status"], "warn")
            _append_detail(result, f"JSON schema validation failed: {exc.message}")


def check_api_endpoints(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Poll configured REST endpoints and return structured health results."""
    results: list[dict[str, Any]] = []

    for endpoint in endpoints:
        expected_status = int(endpoint.get("expected_status", 200))
        timeout_ms = int(endpoint.get("timeout_ms", 3000))
        timeout_seconds = timeout_ms / 1000.0
        result: dict[str, Any] = {
            "name": endpoint.get("name", endpoint["url"]),
            "url": endpoint["url"],
            "method": endpoint.get("method", "GET").upper(),
            "transport": "rest",
            "status": "ok",
        }

        try:
            start = time.monotonic()
            response = requests.request(
                result["method"],
                endpoint["url"],
                timeout=timeout_seconds,
                headers=endpoint.get("headers", {}) or {},
                verify=bool(endpoint.get("verify_tls", True)),
            )
            result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
            result["http_status"] = response.status_code
            result["response_size_bytes"] = len(response.content)

            if response.status_code != expected_status:
                result["status"] = "critical" if response.status_code >= 500 else "warn"
                _append_detail(
                    result,
                    f"Expected HTTP {expected_status}, received HTTP {response.status_code}.",
                )

            _validate_response_content(result, endpoint, response)
        except requests.exceptions.Timeout:
            result["status"] = "critical"
            result["detail"] = f"Timeout after {timeout_ms}ms."
        except requests.exceptions.ConnectionError as exc:
            result["status"] = "critical"
            result["detail"] = f"Connection error: {exc}"
        except Exception as exc:
            result["status"] = "critical"
            result["detail"] = str(exc)

        results.append(result)

    return results
