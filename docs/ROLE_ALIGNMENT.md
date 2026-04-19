# HPE Role Alignment

This project was expanded to map directly to the Hewlett Packard Enterprise high school software engineering internship requirements.

| Job Requirement / Preference | Evidence in This Repo |
| --- | --- |
| Python programming | Core implementation in `monitor.py`, `api_checker.py`, `sys_metrics.py`, and supporting modules |
| REST API work | Configurable API polling, status validation, latency checks, substring checks, and JSON schema validation |
| gRPC awareness | `grpc_checker.py`, `health.proto`, and gRPC endpoint configuration in `config.yaml` |
| Bash scripting | `scripts/run_monitor.sh` and `scripts/smoke_test.sh` |
| Infrastructure as code | `deploy/ansible/site.yml` with Jinja2 templates for config and systemd deployment |
| GitHub version control practices | `.github/workflows/ci.yml`, PR template, and contributing guide |
| Testing and debugging | `tests/` suite, compile step in CI, structured alerts, and NDJSON logs |
| Multi-platform software design | GitHub Actions matrix for Windows, macOS, and Linux plus path normalization in `config_loader.py` |
| Documentation and maintenance procedures | `README.md`, `docs/ARCHITECTURE.md`, `docs/OPERATIONS.md`, and `CONTRIBUTING.md` |
| Communicating architecture and design proposals | Architecture and operations docs explain component responsibilities and tradeoffs |
| Working with QA / DevOps / engineers | CI pipeline, deployment playbook, pull request template, and operational scripts demonstrate cross-functional workflow |
| Awareness of Linux/server environments | systemd service template, Ansible deployment, disk and process metrics, host inventory capture |

## What This Shows About the Role Fit

- You can build with Python in a way that looks like production-minded engineering rather than just classroom exercises.
- You can work across development, testing, deployment, and documentation layers.
- You can think about systems as both code and operations, which fits the edge-to-cloud and server-management flavor of HPE.
- You can communicate your engineering decisions clearly, which matters when working with QA, DevOps, and architecture teams.
