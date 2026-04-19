# API & System Health Monitor

Python-based infrastructure monitor for REST APIs, gRPC services, and local system health, with structured alerting, HTML/JSON reports, automated tests, GitHub Actions CI, and Ansible deployment artifacts.

## Why This Project Exists

I expanded this project to match the technical themes in the Hewlett Packard Enterprise High School Software Engineer Internship:

- Python application development
- REST API and gRPC service awareness
- Linux and systems-oriented thinking
- testing, debugging, and maintenance
- GitHub workflow and CI
- infrastructure as code with Ansible
- documentation and architecture communication

The result is a more complete engineering project instead of a single monitoring script.

## Features

- Configurable REST API health checks with status-code validation
- JSON schema and expected-key validation for API responses
- gRPC transport readiness checks for service endpoints
- Local system metrics: CPU, memory, disk, process count, load average, network I/O
- Host inventory capture for hardware and runtime visibility
- Structured alerting for endpoint and system threshold breaches
- NDJSON logging for each polling cycle
- Jinja2-generated HTML reporting plus JSON summaries
- Multi-platform CI across Windows, macOS, and Linux
- Ansible deployment example with systemd service wiring
- Bash and PowerShell helper scripts for local workflows

## Project Structure

```text
api-system-health-monitor/
|-- .github/
|   |-- pull_request_template.md
|   `-- workflows/ci.yml
|-- deploy/ansible/
|   |-- site.yml
|   `-- templates/
|       |-- config.yaml.j2
|       `-- monitor.service.j2
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- OPERATIONS.md
|   `-- ROLE_ALIGNMENT.md
|-- scripts/
|   |-- run_monitor.ps1
|   |-- run_monitor.sh
|   `-- smoke_test.sh
|-- templates/report.html.j2
|-- tests/
|-- alerting.py
|-- api_checker.py
|-- config.yaml
|-- config_loader.py
|-- grpc_checker.py
|-- health.proto
|-- host_inventory.py
|-- monitor.py
|-- report_generator.py
|-- sys_metrics.py
|-- CONTRIBUTING.md
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Quickstart

```bash
git clone https://github.com/SidChellappan/api-system-health-monitor.git
cd api-system-health-monitor
python -m pip install -r requirements.txt
python -m pytest -v
python monitor.py --config config.yaml run --cycles 1 --report
```

## CLI Usage

Run monitoring cycles:

```bash
python monitor.py --config config.yaml run
python monitor.py --config config.yaml run --cycles 3 --report
```

Generate reports from existing logs:

```bash
python monitor.py --config config.yaml report
```

Export host inventory:

```bash
python monitor.py inventory
python monitor.py inventory --output reports/inventory.json
```

## Configuration Example

```yaml
poll_interval_seconds: 30
max_cycles: 0

system:
  disk_path: "."

api_endpoints:
  - name: "JSONPlaceholder Posts"
    url: "https://jsonplaceholder.typicode.com/posts/1"
    method: GET
    expected_status: 200
    timeout_ms: 2000
    expected_json_keys: [userId, id, title, body]

grpc_endpoints:
  - name: "Local Demo gRPC Server"
    target: "localhost:50051"
    timeout_ms: 750

thresholds:
  cpu_warning_pct: 70
  cpu_critical_pct: 90
  memory_warning_pct: 75
  memory_critical_pct: 90
  disk_warning_pct: 80
  disk_critical_pct: 92
  api_latency_warning_ms: 500
  api_latency_critical_ms: 1500
  grpc_latency_warning_ms: 250
  grpc_latency_critical_ms: 1000

logging:
  log_file: "logs/health_log.ndjson"
  alert_file: "logs/alerts.log"
  report_dir: "reports"
```

## Example Output

```text
2026-04-19 15:40:12,101 [INFO] --- POLL CYCLE #1 ---
2026-04-19 15:40:12,102 [INFO]   [OK      ] API  JSONPlaceholder Posts        status=200 latency=182.4ms
2026-04-19 15:40:12,103 [INFO]   [CRITICAL] gRPC Local Demo gRPC Server       target=localhost:50051 latency=N/Ams
2026-04-19 15:40:12,103 [INFO]   [SYSTEM ] CPU=14.2% MEM=46.8% DISK=52.1% PROCS=241
2026-04-19 15:40:12,103 [ERROR]   --> Local Demo gRPC Server: Channel readiness timed out after 750ms.
```

## Testing

```bash
python -m pytest -v
python -m compileall .
```

The repo includes tests for:

- REST API validation behavior
- threshold-based alerting
- config loading and path normalization
- gRPC readiness checks
- report generation
- system metric collection

## DevOps and Deployment Signals

- GitHub Actions matrix CI: `.github/workflows/ci.yml`
- Ansible deployment example: `deploy/ansible/site.yml`
- Linux service template: `deploy/ansible/templates/monitor.service.j2`
- Bash automation scripts: `scripts/run_monitor.sh`, `scripts/smoke_test.sh`
- PowerShell workflow helper: `scripts/run_monitor.ps1`

## Documentation

- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Operations guide: [docs/OPERATIONS.md](docs/OPERATIONS.md)
- HPE role alignment: [docs/ROLE_ALIGNMENT.md](docs/ROLE_ALIGNMENT.md)
- Contribution workflow: [CONTRIBUTING.md](CONTRIBUTING.md)

## Tech Stack

- Python 3.10+
- `requests`
- `psutil`
- `PyYAML`
- `Jinja2`
- `jsonschema`
- `grpcio`
- `pytest`
- GitHub Actions
- Ansible

## License

MIT License. See [LICENSE](LICENSE).
