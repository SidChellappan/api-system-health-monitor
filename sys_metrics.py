"""System metrics collection."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


def _resolve_disk_path(disk_path: str | None) -> str:
    if disk_path:
        resolved = Path(disk_path).expanduser().resolve()
        return str(resolved)
    cwd = Path.cwd().resolve()
    return cwd.anchor or str(cwd)


def collect_system_metrics(disk_path: str | None = None) -> dict[str, Any]:
    """Collect CPU, memory, disk, and network metrics using psutil."""
    resolved_disk_path = _resolve_disk_path(disk_path)
    cpu = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(resolved_disk_path)
    network = psutil.net_io_counters()
    process_count = len(psutil.pids())

    load_average: tuple[float, float, float] | None
    try:
        load_average = psutil.getloadavg()
    except (AttributeError, OSError):
        load_average = None

    metrics: dict[str, Any] = {
        "cpu_pct": round(cpu, 1),
        "memory_pct": round(memory.percent, 1),
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "swap_pct": round(swap.percent, 1),
        "disk_path": resolved_disk_path,
        "disk_pct": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "net_bytes_sent": network.bytes_sent,
        "net_bytes_recv": network.bytes_recv,
        "process_count": process_count,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    if load_average is not None:
        metrics["load_average"] = {
            "1m": round(load_average[0], 2),
            "5m": round(load_average[1], 2),
            "15m": round(load_average[2], 2),
        }

    return metrics
