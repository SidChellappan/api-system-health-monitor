"""monitor.py - Main polling loop and orchestration for API & System Health Monitor."""

import time
import json
import logging
from datetime import datetime
from pathlib import Path

import yaml

from api_checker import check_api_endpoints
from sys_metrics import collect_system_metrics
from alerting import evaluate_and_alert
from report_generator import append_log_entry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    """Load YAML configuration."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dirs(config: dict) -> None:
    """Create log and report directories if they don't exist."""
    Path(config["logging"]["log_file"]).parent.mkdir(parents=True, exist_ok=True)
    Path(config["logging"]["report_dir"]).mkdir(parents=True, exist_ok=True)


def run_monitor() -> None:
    """Main monitoring loop."""
    config = load_config()
    ensure_dirs(config)
    poll_interval = config.get("poll_interval_seconds", 30)
    log_file = config["logging"]["log_file"]
    cycle = 0

    logger.info("API & System Health Monitor started.")
    logger.info(f"Polling every {poll_interval}s | Log: {log_file}")

    while True:
        cycle += 1
        timestamp = datetime.utcnow().isoformat() + "Z"
        logger.info(f"--- POLL CYCLE #{cycle} [{timestamp}] ---")

        # Collect data
        api_results = check_api_endpoints(config["api_endpoints"])
        sys_results = collect_system_metrics()

        # Evaluate thresholds and dispatch alerts
        alerts = evaluate_and_alert(api_results, sys_results, config["thresholds"])

        # Build log entry
        entry = {
            "cycle": cycle,
            "timestamp": timestamp,
            "api_results": api_results,
            "sys_metrics": sys_results,
            "alerts": alerts,
        }

        # Append to JSON log
        append_log_entry(log_file, entry)

        # Print summary
        for r in api_results:
            status_tag = "[OK]  " if r["status"] == "ok" else f"[{r['status'].upper()}]"
            logger.info(f"  {status_tag} {r['name']:<35} {r.get('http_status', 'N/A')}  |  {r.get('latency_ms', 'N/A')}ms")

        logger.info(f"  CPU: {sys_results['cpu_pct']}%  MEM: {sys_results['memory_pct']}%  DISK: {sys_results['disk_pct']}%")

        if alerts:
            for alert in alerts:
                logger.warning(f"  --> ALERT: {alert}")

        time.sleep(poll_interval)


if __name__ == "__main__":
    run_monitor()
