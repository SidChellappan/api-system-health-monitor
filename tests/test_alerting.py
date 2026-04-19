from __future__ import annotations

from alerting import evaluate_and_alert


def test_alerting_emits_endpoint_and_system_alerts() -> None:
    alerts = evaluate_and_alert(
        api_results=[
            {"name": "REST API", "status": "warn", "latency_ms": 550, "detail": "Schema drift"},
        ],
        grpc_results=[
            {"name": "gRPC API", "status": "critical", "latency_ms": 1200, "detail": "Connection refused"},
        ],
        sys_metrics={"cpu_pct": 91, "memory_pct": 80, "disk_pct": 95},
        thresholds={
            "api_latency_warning_ms": 500,
            "api_latency_critical_ms": 1500,
            "grpc_latency_warning_ms": 250,
            "grpc_latency_critical_ms": 1000,
            "cpu_warning_pct": 70,
            "cpu_critical_pct": 90,
            "memory_warning_pct": 75,
            "memory_critical_pct": 90,
            "disk_warning_pct": 80,
            "disk_critical_pct": 92,
        },
    )

    severities = {alert["severity"] for alert in alerts}
    sources = {alert["source"] for alert in alerts}

    assert "warning" in severities
    assert "critical" in severities
    assert "REST API" in sources
    assert "gRPC API" in sources
    assert "system.cpu" in sources
    assert "system.disk" in sources
