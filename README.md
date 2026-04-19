# API & System Health Monitor

> A Python-based REST API and system health monitoring tool with gRPC awareness, real-time alerting, and exportable diagnostic reports — built for multi-platform infrastructure.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

---

## Overview

The **API & System Health Monitor** is a developer/ops-facing tool that continuously polls REST API endpoints and system-level metrics, evaluates their health status, logs structured results, and generates exportable HTML/JSON reports. Inspired by the kind of infrastructure diagnostics used in enterprise server environments (e.g., HPE ProLiant), this tool is designed to run on any platform and be extended with minimal effort.

---

## Features

- **REST API Health Polling** — Configure any number of endpoints; checks HTTP status codes, response times, and JSON schema validity
- **System Metrics Collection** — CPU usage, memory, disk I/O, and network latency via `psutil`
- **Threshold-Based Alerting** — Define warning/critical thresholds; alerts printed to console and logged to file
- **Structured JSON Logging** — Every poll cycle produces a timestamped JSON entry for downstream analysis
- **HTML Report Generation** — Single-command export of a clean, color-coded diagnostic report
- **Multi-Platform Support** — Tested on Linux (Ubuntu 22.04), Windows 10/11, macOS 13+
- **Configurable via YAML** — No code changes needed to add endpoints or change thresholds
- **Extensible gRPC Stub** — Placeholder gRPC service definition (`health.proto`) for enterprise integration

---

## Project Structure

```
api-system-health-monitor/
├── monitor.py              # Main polling loop and orchestration
├── api_checker.py          # REST endpoint health checks
├── sys_metrics.py          # System resource collection (psutil)
├── alerting.py             # Threshold evaluation and alert dispatch
├── report_generator.py     # HTML + JSON report export
├── config.yaml             # User-facing configuration file
├── health.proto            # gRPC service definition (stub)
├── requirements.txt        # Python dependencies
├── tests/
│   ├── test_api_checker.py
│   └── test_sys_metrics.py
└── README.md
```

---

## Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/SidChellappan/api-system-health-monitor.git
cd api-system-health-monitor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Edit config.yaml with your endpoints and thresholds

# 4. Run the monitor
python monitor.py

# 5. Generate a report
python report_generator.py --output report.html
```

---

## Configuration (`config.yaml`)

```yaml
poll_interval_seconds: 30

api_endpoints:
  - name: "JSONPlaceholder Posts"
    url: "https://jsonplaceholder.typicode.com/posts/1"
    method: GET
    expected_status: 200
    timeout_ms: 2000
  - name: "HTTPBin Status"
    url: "https://httpbin.org/status/200"
    method: GET
    expected_status: 200
    timeout_ms: 1500

thresholds:
  cpu_warning_pct: 70
  cpu_critical_pct: 90
  memory_warning_pct: 75
  memory_critical_pct: 90
  api_latency_warning_ms: 500
  api_latency_critical_ms: 1500

logging:
  log_file: "logs/health_log.json"
  report_dir: "reports/"
```

---

## Sample Output

```
[2026-04-19 14:32:01] POLL CYCLE #12
  [OK]   JSONPlaceholder Posts     200  |  312ms
  [WARN] HTTPBin Status            200  |  521ms  (latency > 500ms threshold)
  [OK]   CPU Usage                 43.2%
  [OK]   Memory Usage              61.8%
  [OK]   Disk Usage                48.3%
  --> Alert dispatched: HTTPBin latency exceeded warning threshold
```

---

## Tech Stack

| Component         | Technology              |
|-------------------|-------------------------|
| Language          | Python 3.10+            |
| HTTP Requests     | `requests`, `httpx`     |
| System Metrics    | `psutil`                |
| Config Parsing    | `PyYAML`                |
| Report Templating | `Jinja2`                |
| gRPC Stub         | `grpcio`, `protobuf`    |
| Testing           | `pytest`                |

---

## gRPC Extension

The included `health.proto` defines a `HealthCheckService` with a `Check` RPC — following the [gRPC Health Checking Protocol](https://grpc.io/docs/guides/health-checking/). This makes the monitor easy to integrate into larger service meshes or HPE-style server management stacks.

```protobuf
service HealthCheckService {
  rpc Check (HealthCheckRequest) returns (HealthCheckResponse);
  rpc Watch (HealthCheckRequest) returns (stream HealthCheckResponse);
}
```

---

## Testing

```bash
pytest tests/ -v
```

---

## Author

**Siddharth Chellappan** — Rising Junior, Princeton High School  
GitHub: [@SidChellappan](https://github.com/SidChellappan)

---

## License

MIT License — see `LICENSE` for details.
