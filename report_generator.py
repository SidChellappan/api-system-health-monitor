"""Log management and report generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def append_log_entry(log_file: str, entry: dict[str, Any]) -> None:
    """Append a single monitoring cycle entry to an NDJSON log."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def load_log_entries(log_file: str) -> list[dict[str, Any]]:
    """Load monitoring entries from an NDJSON log file."""
    log_path = Path(log_file)
    if not log_path.exists():
        return []

    entries: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _build_endpoint_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for result in results:
        stats = grouped.setdefault(
            result["name"],
            {
                "name": result["name"],
                "transport": result.get("transport", "unknown"),
                "checks": 0,
                "non_ok_checks": 0,
                "latencies": [],
                "last_status": "unknown",
                "last_detail": "",
            },
        )
        stats["checks"] += 1
        if result.get("status") != "ok":
            stats["non_ok_checks"] += 1
        if result.get("latency_ms") is not None:
            stats["latencies"].append(float(result["latency_ms"]))
        stats["last_status"] = result.get("status", "unknown")
        stats["last_detail"] = result.get("detail", "")

    summary: list[dict[str, Any]] = []
    for stats in grouped.values():
        checks = stats["checks"]
        failures = stats["non_ok_checks"]
        summary.append(
            {
                "name": stats["name"],
                "transport": stats["transport"],
                "checks": checks,
                "availability_pct": round(((checks - failures) / checks) * 100, 1) if checks else 0.0,
                "avg_latency_ms": round(mean(stats["latencies"]), 1) if stats["latencies"] else None,
                "last_status": stats["last_status"],
                "last_detail": stats["last_detail"],
            }
        )
    return sorted(summary, key=lambda item: (item["transport"], item["name"]))


def build_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a report summary from monitoring entries."""
    latest = entries[-1] if entries else {}
    all_api_results = [result for entry in entries for result in entry.get("api_results", [])]
    all_grpc_results = [result for entry in entries for result in entry.get("grpc_results", [])]
    all_alerts = [alert for entry in entries for alert in entry.get("alerts", [])]

    critical_alerts = [alert for alert in all_alerts if alert.get("severity") == "critical"]
    warning_alerts = [alert for alert in all_alerts if alert.get("severity") == "warning"]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cycle_count": len(entries),
        "latest_cycle": latest.get("cycle"),
        "latest_timestamp": latest.get("timestamp"),
        "latest_system_metrics": latest.get("sys_metrics", {}),
        "host": latest.get("host", {}),
        "api_summary": _build_endpoint_summary(all_api_results),
        "grpc_summary": _build_endpoint_summary(all_grpc_results),
        "alert_count": len(all_alerts),
        "critical_alert_count": len(critical_alerts),
        "warning_alert_count": len(warning_alerts),
        "recent_entries": entries[-25:],
    }


def _jinja_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def generate_html_report(log_file: str, output_path: str) -> dict[str, Any]:
    """Generate an HTML report from an NDJSON log file."""
    entries = load_log_entries(log_file)
    summary = build_summary(entries)

    environment = _jinja_environment()
    template = environment.get_template("report.html.j2")
    html = template.render(summary=summary)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return summary


def generate_json_summary(log_file: str, output_path: str) -> dict[str, Any]:
    """Generate a JSON summary report from an NDJSON log file."""
    entries = load_log_entries(log_file)
    summary = build_summary(entries)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
