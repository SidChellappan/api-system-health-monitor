"""Host inventory collection for diagnostic reports."""

from __future__ import annotations

from datetime import datetime, timezone
import platform
import socket

import psutil


def collect_host_inventory() -> dict[str, object]:
    """Collect a snapshot of host and runtime information."""
    virtual_memory = psutil.virtual_memory()
    partitions = [
        {
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
        }
        for partition in psutil.disk_partitions(all=False)
    ]

    return {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python_version": platform.python_version(),
        "logical_cores": psutil.cpu_count() or 0,
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "total_memory_gb": round(virtual_memory.total / (1024**3), 2),
        "boot_time_utc": datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat(),
        "network_interfaces": sorted(psutil.net_if_addrs().keys()),
        "disk_partitions": partitions,
    }
