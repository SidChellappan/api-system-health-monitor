"""report_generator.py - JSON log management and HTML report export."""

import json
import argparse
from pathlib import Path
from datetime import datetime


def append_log_entry(log_file: str, entry: dict) -> None:
    """Append a single poll cycle entry to the NDJSON log file."""
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_log_entries(log_file: str) -> list[dict]:
    """Load all entries from the NDJSON log file."""
    entries = []
    path = Path(log_file)
    if not path.exists():
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def generate_html_report(log_file: str, output_path: str) -> None:
    """Generate a color-coded HTML diagnostic report from log entries."""
    entries = load_log_entries(log_file)
    rows = ""
    for e in entries[-100:]:  # Last 100 cycles
        ts = e.get("timestamp", "N/A")
        cycle = e.get("cycle", "?")
        alerts = e.get("alerts", [])
        sys = e.get("sys_metrics", {})
        api_summary = ", ".join(
            f"{r['name']}: {r.get('status','?').upper()}"
            for r in e.get("api_results", [])
        )
        alert_class = "critical" if any("CRITICAL" in a for a in alerts) else (
            "warn" if alerts else "ok"
        )
        rows += f"""
        <tr class="{alert_class}">
          <td>{cycle}</td>
          <td>{ts}</td>
          <td>{api_summary}</td>
          <td>{sys.get('cpu_pct', 'N/A')}%</td>
          <td>{sys.get('memory_pct', 'N/A')}%</td>
          <td>{sys.get('disk_pct', 'N/A')}%</td>
          <td>{'; '.join(alerts) if alerts else 'None'}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>API &amp; System Health Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
    h1 {{ color: #333; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th {{ background: #0078d4; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 8px 10px; border-bottom: 1px solid #ddd; }}
    tr.ok {{ background: #e6ffe6; }}
    tr.warn {{ background: #fff8cc; }}
    tr.critical {{ background: #ffe6e6; }}
    .footer {{ margin-top: 20px; font-size: 0.85em; color: #666; }}
  </style>
</head>
<body>
  <h1>API &amp; System Health Monitor - Diagnostic Report</h1>
  <p>Generated: {datetime.utcnow().isoformat()}Z | Cycles shown: {len(entries)}</p>
  <table>
    <thead>
      <tr>
        <th>Cycle</th>
        <th>Timestamp</th>
        <th>API Status</th>
        <th>CPU</th>
        <th>Memory</th>
        <th>Disk</th>
        <th>Alerts</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <div class="footer">API &amp; System Health Monitor &mdash; Siddharth Chellappan &mdash; github.com/SidChellappan</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate health monitor HTML report")
    parser.add_argument("--log", default="logs/health_log.json", help="Path to NDJSON log")
    parser.add_argument("--output", default="reports/report.html", help="Output HTML path")
    args = parser.parse_args()
    generate_html_report(args.log, args.output)
