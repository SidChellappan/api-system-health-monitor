from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from report_generator import append_log_entry, generate_html_report, generate_json_summary


def test_report_generator_creates_html_and_json_outputs() -> None:
    tmp_path = Path.cwd() / "tests_runtime" / f"report_generator_{uuid4().hex}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    log_path = tmp_path / "health.ndjson"
    entry = {
        "cycle": 1,
        "timestamp": "2026-04-19T15:00:00+00:00",
        "host": {"hostname": "demo-host", "python_version": "3.11", "network_interfaces": ["Ethernet"], "platform": "Windows", "physical_cores": 4, "logical_cores": 8, "total_memory_gb": 16},
        "api_results": [{"name": "REST API", "transport": "rest", "status": "ok", "latency_ms": 120.0}],
        "grpc_results": [{"name": "gRPC API", "transport": "grpc", "status": "critical", "detail": "Connection refused"}],
        "sys_metrics": {"cpu_pct": 20, "memory_pct": 45, "disk_pct": 50, "disk_path": "C:/", "process_count": 200, "net_bytes_sent": 10, "net_bytes_recv": 11},
        "alerts": [{"severity": "critical", "source": "gRPC API", "message": "Connection refused"}],
    }
    append_log_entry(str(log_path), entry)

    html_path = tmp_path / "report.html"
    json_path = tmp_path / "summary.json"

    summary = generate_html_report(str(log_path), str(html_path))
    generate_json_summary(str(log_path), str(json_path))

    assert summary["cycle_count"] == 1
    assert html_path.exists()
    assert json_path.exists()
    assert "REST API" in html_path.read_text(encoding="utf-8")
