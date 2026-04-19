from __future__ import annotations

import grpc

from grpc_checker import check_grpc_endpoints


class FakeChannel:
    def close(self) -> None:
        return None


class ReadyFuture:
    def result(self, timeout: float) -> None:
        return None


class TimeoutFuture:
    def result(self, timeout: float) -> None:
        raise grpc.FutureTimeoutError()


def test_grpc_checker_reports_ready_channel(monkeypatch) -> None:
    monkeypatch.setattr(grpc, "insecure_channel", lambda target: FakeChannel())
    monkeypatch.setattr(grpc, "channel_ready_future", lambda channel: ReadyFuture())

    results = check_grpc_endpoints([{"name": "Demo gRPC", "target": "localhost:50051"}])

    assert results[0]["status"] == "ok"
    assert results[0]["target"] == "localhost:50051"


def test_grpc_checker_reports_timeout(monkeypatch) -> None:
    monkeypatch.setattr(grpc, "insecure_channel", lambda target: FakeChannel())
    monkeypatch.setattr(grpc, "channel_ready_future", lambda channel: TimeoutFuture())

    results = check_grpc_endpoints([{"name": "Demo gRPC", "target": "localhost:50051", "timeout_ms": 25}])

    assert results[0]["status"] == "critical"
    assert "timed out" in results[0]["detail"]
