"""alerting.py - Threshold evaluation and alert dispatch."""

from typing import Any


def evaluate_and_alert(
    api_results: list[dict[str, Any]],
    sys_metrics: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[str]:
    """Compare metrics against thresholds and return a list of alert messages."""
    alerts = []

    # --- API latency alerts ---
    warn_ms = thresholds.get("api_latency_warning_ms", 500)
    crit_ms = thresholds.get("api_latency_critical_ms", 1500)
    for r in api_results:
        latency = r.get("latency_ms")
        if latency is None:
            continue
        if latency >= crit_ms:
            alerts.append(f"CRITICAL: {r['name']} latency {latency}ms >= {crit_ms}ms")
        elif latency >= warn_ms:
            alerts.append(f"WARNING: {r['name']} latency {latency}ms >= {warn_ms}ms")
        if r["status"] == "critical":
            alerts.append(f"CRITICAL: {r['name']} unreachable - {r.get('detail', '')}")

    # --- CPU alerts ---
    cpu = sys_metrics.get("cpu_pct", 0)
    if cpu >= thresholds.get("cpu_critical_pct", 90):
        alerts.append(f"CRITICAL: CPU usage {cpu}% >= {thresholds['cpu_critical_pct']}%")
    elif cpu >= thresholds.get("cpu_warning_pct", 70):
        alerts.append(f"WARNING: CPU usage {cpu}% >= {thresholds['cpu_warning_pct']}%")

    # --- Memory alerts ---
    mem = sys_metrics.get("memory_pct", 0)
    if mem >= thresholds.get("memory_critical_pct", 90):
        alerts.append(f"CRITICAL: Memory usage {mem}% >= {thresholds['memory_critical_pct']}%")
    elif mem >= thresholds.get("memory_warning_pct", 75):
        alerts.append(f"WARNING: Memory usage {mem}% >= {thresholds['memory_warning_pct']}%")

    return alerts
