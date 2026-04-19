"""gRPC transport health checks."""

from __future__ import annotations

import time
from typing import Any

import grpc


def check_grpc_endpoints(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check whether configured gRPC targets accept connections."""
    results: list[dict[str, Any]] = []

    for endpoint in endpoints:
        timeout_ms = int(endpoint.get("timeout_ms", 1500))
        timeout_seconds = timeout_ms / 1000.0
        secure = bool(endpoint.get("secure", False))
        channel: grpc.Channel | None = None
        result: dict[str, Any] = {
            "name": endpoint.get("name", endpoint["target"]),
            "target": endpoint["target"],
            "transport": "grpc",
            "status": "ok",
        }

        try:
            start = time.monotonic()
            if secure:
                channel = grpc.secure_channel(
                    endpoint["target"],
                    grpc.ssl_channel_credentials(),
                )
            else:
                channel = grpc.insecure_channel(endpoint["target"])

            grpc.channel_ready_future(channel).result(timeout=timeout_seconds)
            result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
            result["detail"] = "Channel became ready within timeout."
        except grpc.FutureTimeoutError:
            result["status"] = "critical"
            result["detail"] = f"Channel readiness timed out after {timeout_ms}ms."
        except Exception as exc:
            result["status"] = "critical"
            result["detail"] = f"gRPC connection error: {exc}"
        finally:
            if channel is not None:
                channel.close()

        results.append(result)

    return results
