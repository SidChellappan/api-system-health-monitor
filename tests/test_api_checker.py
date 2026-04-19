from __future__ import annotations

from types import SimpleNamespace

import requests

from api_checker import check_api_endpoints


class FakeResponse:
    def __init__(self, status_code: int, payload: dict, text: str | None = None) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text or str(payload)
        self.content = self.text.encode("utf-8")

    def json(self) -> dict:
        return self._payload


def test_api_checker_reports_ok_when_response_matches_expectations(monkeypatch) -> None:
    def fake_request(*args, **kwargs):
        return FakeResponse(
            200,
            {"userId": 1, "id": 1, "title": "demo", "body": "body"},
            text='{"current_user_url":"https://api.github.com/user"}',
        )

    monkeypatch.setattr(requests, "request", fake_request)

    results = check_api_endpoints(
        [
            {
                "name": "Demo API",
                "url": "https://example.com",
                "method": "GET",
                "expected_status": 200,
                "timeout_ms": 500,
                "expected_json_keys": ["userId", "id", "title", "body"],
                "expected_json_schema": {
                    "type": "object",
                    "required": ["userId", "id", "title", "body"],
                },
            }
        ]
    )

    assert results[0]["status"] == "ok"
    assert results[0]["http_status"] == 200
    assert results[0]["response_size_bytes"] > 0


def test_api_checker_warns_when_json_shape_does_not_match(monkeypatch) -> None:
    monkeypatch.setattr(
        requests,
        "request",
        lambda *args, **kwargs: FakeResponse(200, {"id": 1, "title": "missing fields"}),
    )

    results = check_api_endpoints(
        [
            {
                "name": "Bad JSON",
                "url": "https://example.com",
                "expected_json_keys": ["id", "userId"],
            }
        ]
    )

    assert results[0]["status"] == "warn"
    assert "Missing expected JSON keys" in results[0]["detail"]


def test_api_checker_marks_timeout_as_critical(monkeypatch) -> None:
    def fake_request(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "request", fake_request)

    results = check_api_endpoints([{"name": "Slow API", "url": "https://example.com", "timeout_ms": 10}])

    assert results[0]["status"] == "critical"
    assert "Timeout" in results[0]["detail"]
