from __future__ import annotations

from types import SimpleNamespace

import psutil

from sys_metrics import collect_system_metrics


def test_collect_system_metrics_returns_expected_fields(monkeypatch) -> None:
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval: 25.4)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(percent=40.1, used=8 * 1024**3, total=16 * 1024**3))
    monkeypatch.setattr(psutil, "swap_memory", lambda: SimpleNamespace(percent=3.5))
    monkeypatch.setattr(psutil, "disk_usage", lambda path: SimpleNamespace(percent=52.2, used=200 * 1024**3, total=400 * 1024**3))
    monkeypatch.setattr(psutil, "net_io_counters", lambda: SimpleNamespace(bytes_sent=1000, bytes_recv=2000))
    monkeypatch.setattr(psutil, "pids", lambda: [1, 2, 3])
    monkeypatch.setattr(psutil, "getloadavg", lambda: (0.5, 0.7, 0.9))

    metrics = collect_system_metrics(".")

    assert metrics["cpu_pct"] == 25.4
    assert metrics["memory_pct"] == 40.1
    assert metrics["disk_pct"] == 52.2
    assert metrics["process_count"] == 3
    assert metrics["load_average"]["5m"] == 0.7
