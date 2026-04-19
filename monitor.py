"""Command-line entry point for the API & System Health Monitor."""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from alerting import evaluate_and_alert
from api_checker import check_api_endpoints
from config_loader import load_config
from grpc_checker import check_grpc_endpoints
from host_inventory import collect_host_inventory
from report_generator import append_log_entry, generate_html_report, generate_json_summary
from sys_metrics import collect_system_metrics


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def ensure_dirs(config: dict) -> None:
    """Create log and report directories if they do not exist."""
    Path(config["logging"]["log_file"]).parent.mkdir(parents=True, exist_ok=True)
    Path(config["logging"]["alert_file"]).parent.mkdir(parents=True, exist_ok=True)
    Path(config["logging"]["report_dir"]).mkdir(parents=True, exist_ok=True)


def write_alert_log(alert_file: str, timestamp: str, alerts: list[dict[str, str]]) -> None:
    """Append structured alerts to a line-oriented alert log."""
    if not alerts:
        return
    with Path(alert_file).open("a", encoding="utf-8") as handle:
        for alert in alerts:
            handle.write(
                f"{timestamp} [{alert['severity'].upper()}] {alert['source']}: {alert['message']}\n"
            )


def print_cycle_summary(
    cycle: int,
    api_results: list[dict],
    grpc_results: list[dict],
    sys_results: dict,
    alerts: list[dict],
) -> None:
    """Emit a concise human-readable cycle summary."""
    logger.info("--- POLL CYCLE #%s ---", cycle)
    for result in api_results:
        logger.info(
            "  [%-8s] API  %-28s status=%s latency=%sms",
            result.get("status", "?").upper(),
            result["name"],
            result.get("http_status", "N/A"),
            result.get("latency_ms", "N/A"),
        )

    for result in grpc_results:
        logger.info(
            "  [%-8s] gRPC %-28s target=%s latency=%sms",
            result.get("status", "?").upper(),
            result["name"],
            result.get("target", "N/A"),
            result.get("latency_ms", "N/A"),
        )

    logger.info(
        "  [SYSTEM ] CPU=%s%% MEM=%s%% DISK=%s%% PROCS=%s",
        sys_results["cpu_pct"],
        sys_results["memory_pct"],
        sys_results["disk_pct"],
        sys_results["process_count"],
    )

    for alert in alerts:
        log_method = logger.warning if alert["severity"] == "warning" else logger.error
        log_method("  --> %s: %s", alert["source"], alert["message"])


def run_monitor(config_path: str, cycle_override: int | None = None, auto_report: bool = False) -> None:
    """Run the monitor according to the provided configuration."""
    config = load_config(config_path)
    ensure_dirs(config)

    poll_interval = config["poll_interval_seconds"]
    cycle_limit = cycle_override if cycle_override is not None else config["max_cycles"]
    log_file = config["logging"]["log_file"]
    report_dir = Path(config["logging"]["report_dir"])
    host_inventory = collect_host_inventory()

    logger.info("API & System Health Monitor started.")
    logger.info("Polling every %ss | Log file: %s", poll_interval, log_file)
    if cycle_limit:
        logger.info("Cycle limit enabled: %s", cycle_limit)

    cycle = 0
    while True:
        cycle += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        api_results = check_api_endpoints(config["api_endpoints"])
        grpc_results = check_grpc_endpoints(config["grpc_endpoints"])
        sys_results = collect_system_metrics(config["system"]["disk_path"])
        alerts = evaluate_and_alert(api_results, grpc_results, sys_results, config["thresholds"])

        entry = {
            "cycle": cycle,
            "timestamp": timestamp,
            "host": host_inventory,
            "api_results": api_results,
            "grpc_results": grpc_results,
            "sys_metrics": sys_results,
            "alerts": alerts,
        }
        append_log_entry(log_file, entry)
        write_alert_log(config["logging"]["alert_file"], timestamp, alerts)
        print_cycle_summary(cycle, api_results, grpc_results, sys_results, alerts)

        if cycle_limit and cycle >= cycle_limit:
            break
        time.sleep(poll_interval)

    if auto_report:
        html_path = report_dir / "report.html"
        json_path = report_dir / "summary.json"
        generate_html_report(log_file, str(html_path))
        generate_json_summary(log_file, str(json_path))
        logger.info("Generated report artifacts at %s", report_dir)


def generate_reports(config_path: str, log_file: str | None = None, output_dir: str | None = None) -> None:
    """Generate HTML and JSON report artifacts."""
    config = load_config(config_path)
    ensure_dirs(config)
    resolved_log = log_file or config["logging"]["log_file"]
    resolved_output_dir = Path(output_dir or config["logging"]["report_dir"])
    generate_html_report(resolved_log, str(resolved_output_dir / "report.html"))
    generate_json_summary(resolved_log, str(resolved_output_dir / "summary.json"))
    logger.info("Report artifacts written to %s", resolved_output_dir)


def export_inventory(output_path: str | None = None) -> None:
    """Print or persist the current host inventory."""
    inventory = collect_host_inventory()
    serialized_inventory = json.dumps(inventory, indent=2)
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialized_inventory, encoding="utf-8")
        logger.info("Inventory written to %s", destination)
        return
    logger.info("Host inventory:\n%s", serialized_inventory)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="API & System Health Monitor")
    parser.add_argument("--config", default="config.yaml", help="Path to the YAML configuration file.")

    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run monitoring cycles.")
    run_parser.add_argument("--cycles", type=int, default=None, help="Override configured cycle limit.")
    run_parser.add_argument("--report", action="store_true", help="Generate reports when finished.")

    report_parser = subparsers.add_parser("report", help="Generate HTML and JSON reports from logs.")
    report_parser.add_argument("--log", default=None, help="Override the log file to summarize.")
    report_parser.add_argument("--output-dir", default=None, help="Directory for generated report artifacts.")

    inventory_parser = subparsers.add_parser("inventory", help="Export host inventory metadata.")
    inventory_parser.add_argument("--output", default=None, help="Optional path to save the inventory snapshot.")

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "report":
        generate_reports(args.config, log_file=args.log, output_dir=args.output_dir)
    elif args.command == "inventory":
        export_inventory(args.output)
    else:
        cycles = getattr(args, "cycles", None)
        auto_report = getattr(args, "report", False)
        run_monitor(args.config, cycle_override=cycles, auto_report=auto_report)


if __name__ == "__main__":
    main()
