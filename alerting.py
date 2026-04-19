"""Threshold evaluation and structured alert creation."""

from __future__ import annotations

from typing import Any


def _make_alert(severity: str, source: str, message: str) -> dict[str, str]:
    return {"severity": severity, "source": source, "message": message}


def _evaluate_endpoint_status(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    alerts: list[dict[str, str]] = []
    for result in results:
        status = result.get("status", "ok")
        if status == "warn":
            alerts.append(
                _make_alert(
                    "warning",
                    result.get("name", "endpoint"),
                    result.get("detail", "Endpoint returned a warning state."),
                )
            )
        elif status == "critical":
            alerts.append(
                _make_alert(
                    "critical",
                    result.get("name", "endpoint"),
                    result.get("detail", "Endpoint check failed."),
                )
            )
    return alerts


def evaluate_and_alert(
    api_results: list[dict[str, Any]],
    grpc_results: list[dict[str, Any]],
    sys_metrics: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[dict[str, str]]:
    """Compare metrics against thresholds and return structured alerts."""
    alerts = _evaluate_endpoint_status(api_results) + _evaluate_endpoint_status(grpc_results)

    api_warn_ms = float(thresholds.get("api_latency_warning_ms", 500))
    api_critical_ms = float(thresholds.get("api_latency_critical_ms", 1500))
    for result in api_results:
        latency = result.get("latency_ms")
        if latency is None:
            continue
        if latency >= api_critical_ms:
            alerts.append(
                _make_alert(
                    "critical",
                    result["name"],
                    f"API latency {latency}ms exceeded critical threshold {api_critical_ms}ms.",
                )
            )
        elif latency >= api_warn_ms:
            alerts.append(
                _make_alert(
                    "warning",
                    result["name"],
                    f"API latency {latency}ms exceeded warning threshold {api_warn_ms}ms.",
                )
            )

    grpc_warn_ms = float(thresholds.get("grpc_latency_warning_ms", 250))
    grpc_critical_ms = float(thresholds.get("grpc_latency_critical_ms", 1000))
    for result in grpc_results:
        latency = result.get("latency_ms")
        if latency is None:
            continue
        if latency >= grpc_critical_ms:
            alerts.append(
                _make_alert(
                    "critical",
                    result["name"],
                    f"gRPC latency {latency}ms exceeded critical threshold {grpc_critical_ms}ms.",
                )
            )
        elif latency >= grpc_warn_ms:
            alerts.append(
                _make_alert(
                    "warning",
                    result["name"],
                    f"gRPC latency {latency}ms exceeded warning threshold {grpc_warn_ms}ms.",
                )
            )

    cpu_pct = float(sys_metrics.get("cpu_pct", 0))
    if cpu_pct >= float(thresholds.get("cpu_critical_pct", 90)):
        alerts.append(
            _make_alert(
                "critical",
                "system.cpu",
                f"CPU usage {cpu_pct}% exceeded critical threshold {thresholds['cpu_critical_pct']}%.",
            )
        )
    elif cpu_pct >= float(thresholds.get("cpu_warning_pct", 70)):
        alerts.append(
            _make_alert(
                "warning",
                "system.cpu",
                f"CPU usage {cpu_pct}% exceeded warning threshold {thresholds['cpu_warning_pct']}%.",
            )
        )

    memory_pct = float(sys_metrics.get("memory_pct", 0))
    if memory_pct >= float(thresholds.get("memory_critical_pct", 90)):
        alerts.append(
            _make_alert(
                "critical",
                "system.memory",
                f"Memory usage {memory_pct}% exceeded critical threshold {thresholds['memory_critical_pct']}%.",
            )
        )
    elif memory_pct >= float(thresholds.get("memory_warning_pct", 75)):
        alerts.append(
            _make_alert(
                "warning",
                "system.memory",
                f"Memory usage {memory_pct}% exceeded warning threshold {thresholds['memory_warning_pct']}%.",
            )
        )

    disk_pct = float(sys_metrics.get("disk_pct", 0))
    if disk_pct >= float(thresholds.get("disk_critical_pct", 92)):
        alerts.append(
            _make_alert(
                "critical",
                "system.disk",
                f"Disk usage {disk_pct}% exceeded critical threshold {thresholds['disk_critical_pct']}%.",
            )
        )
    elif disk_pct >= float(thresholds.get("disk_warning_pct", 80)):
        alerts.append(
            _make_alert(
                "warning",
                "system.disk",
                f"Disk usage {disk_pct}% exceeded warning threshold {thresholds['disk_warning_pct']}%.",
            )
        )

    return alerts
