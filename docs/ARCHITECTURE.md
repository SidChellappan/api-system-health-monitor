# Architecture

## Goal

This project is a lightweight infrastructure observability tool designed to demonstrate software engineering, systems thinking, and operational discipline for backend and platform-oriented internships.

## Monitoring Flow

1. `monitor.py` loads and validates YAML configuration through `config_loader.py`.
2. REST targets are checked through `api_checker.py`.
3. gRPC targets are checked through `grpc_checker.py`.
4. Local machine metrics and host inventory are captured through `sys_metrics.py` and `host_inventory.py`.
5. `alerting.py` compares results against configured thresholds and emits structured alerts.
6. `report_generator.py` appends NDJSON logs and renders HTML and JSON summaries for review.

## Components

- `monitor.py`: CLI entry point, cycle orchestration, alert log writing, and report generation.
- `config_loader.py`: Schema-lite validation, default handling, and path normalization.
- `api_checker.py`: REST checks, latency capture, expected status validation, expected substring checks, and JSON schema validation.
- `grpc_checker.py`: gRPC channel readiness checks for transport-level service validation.
- `sys_metrics.py`: CPU, memory, disk, network, load average, and process count sampling.
- `host_inventory.py`: Hardware and runtime metadata for diagnostics and deployment context.
- `report_generator.py`: NDJSON loading, summary aggregation, and Jinja2-based HTML rendering.

## Design Choices

- Configuration stays in YAML so changing targets does not require code edits.
- Logs use NDJSON so each cycle is append-only and easy to consume with scripts or future pipelines.
- Reports separate data capture from presentation, which mirrors how production systems often store telemetry before visualization.
- GitHub Actions and pytest provide a QA signal for multi-platform reliability.
- Ansible templates show how the monitor could be deployed as infrastructure-as-code.

## Future Extensions

- Add authenticated API checks with secret management.
- Add full gRPC health RPC checks against generated stubs.
- Add trend charts and time-window alert suppression.
- Add container packaging for server or lab deployment scenarios.
