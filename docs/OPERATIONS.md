# Operations Guide

## Local Setup

```bash
python -m pip install -r requirements.txt
python -m pytest -v
python monitor.py --config config.yaml run --cycles 1 --report
```

## Useful Commands

- `python monitor.py --config config.yaml run`
- `python monitor.py --config config.yaml run --cycles 1 --report`
- `python monitor.py --config config.yaml report`
- `python monitor.py inventory`

## Runtime Outputs

- `logs/health_log.ndjson`: append-only monitoring history
- `logs/alerts.log`: human-readable alerts
- `reports/report.html`: formatted diagnostic report
- `reports/summary.json`: machine-readable summary

## Maintenance Checklist

1. Update endpoint definitions in `config.yaml`.
2. Re-run `python -m pytest -v` after behavior changes.
3. Regenerate reports after collecting new data.
4. Review `.github/workflows/ci.yml` when adding new dependencies or OS-specific behavior.
5. Update the Ansible template if deployment expectations change.

## Troubleshooting

- If an endpoint times out, confirm network access and timeout thresholds.
- If disk metrics fail, confirm `system.disk_path` points to a valid location on the host.
- If gRPC checks fail, verify the target port is exposed and accepting connections.
- If reports do not render, confirm `templates/report.html.j2` is present and Jinja2 is installed.
