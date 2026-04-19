"""sys_metrics.py - System resource metrics collection."""

import psutil


def collect_system_metrics() -> dict:
    """Collect CPU, memory, and disk metrics using psutil."""
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net_before = psutil.net_io_counters()

    return {
        "cpu_pct": round(cpu, 1),
        "memory_pct": round(mem.percent, 1),
        "memory_used_gb": round(mem.used / (1024 ** 3), 2),
        "memory_total_gb": round(mem.total / (1024 ** 3), 2),
        "disk_pct": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "net_bytes_sent": net_before.bytes_sent,
        "net_bytes_recv": net_before.bytes_recv,
    }
