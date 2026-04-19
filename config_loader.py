"""Configuration loading and validation for the health monitor."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_THRESHOLDS: dict[str, float] = {
    "cpu_warning_pct": 70,
    "cpu_critical_pct": 90,
    "memory_warning_pct": 75,
    "memory_critical_pct": 90,
    "disk_warning_pct": 80,
    "disk_critical_pct": 92,
    "api_latency_warning_ms": 500,
    "api_latency_critical_ms": 1500,
    "grpc_latency_warning_ms": 250,
    "grpc_latency_critical_ms": 1000,
}

DEFAULT_LOGGING: dict[str, str] = {
    "log_file": "logs/health_log.ndjson",
    "alert_file": "logs/alerts.log",
    "report_dir": "reports",
}


def _resolve_output_path(base_path: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base_path / path).resolve())


def _validate_required_string(container: dict[str, Any], key: str, context: str) -> str:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} requires a non-empty '{key}' value.")
    return value.strip()


def _load_schema_file(schema_file: str, base_path: Path) -> dict[str, Any]:
    schema_path = Path(schema_file)
    if not schema_path.is_absolute():
        schema_path = (base_path / schema_path).resolve()
    with schema_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Schema file '{schema_path}' must contain a JSON/YAML object.")
    return loaded


def _normalize_api_endpoints(endpoints: Any, base_path: Path) -> list[dict[str, Any]]:
    if endpoints is None:
        return []
    if not isinstance(endpoints, list):
        raise ValueError("'api_endpoints' must be a list.")

    normalized: list[dict[str, Any]] = []
    for index, endpoint in enumerate(endpoints, start=1):
        context = f"api_endpoints[{index}]"
        if not isinstance(endpoint, dict):
            raise ValueError(f"{context} must be a mapping.")

        normalized_endpoint: dict[str, Any] = {
            "name": endpoint.get("name") or _validate_required_string(endpoint, "url", context),
            "url": _validate_required_string(endpoint, "url", context),
            "method": str(endpoint.get("method", "GET")).upper(),
            "expected_status": int(endpoint.get("expected_status", 200)),
            "timeout_ms": int(endpoint.get("timeout_ms", 3000)),
            "verify_tls": bool(endpoint.get("verify_tls", True)),
            "headers": endpoint.get("headers", {}) or {},
            "expected_json_keys": endpoint.get("expected_json_keys", []) or [],
            "expected_substring": endpoint.get("expected_substring"),
        }

        inline_schema = endpoint.get("expected_json_schema")
        schema_file = endpoint.get("schema_file")
        if inline_schema and not isinstance(inline_schema, dict):
            raise ValueError(f"{context}.expected_json_schema must be an object.")
        if schema_file is not None and not isinstance(schema_file, str):
            raise ValueError(f"{context}.schema_file must be a string path.")
        if inline_schema:
            normalized_endpoint["expected_json_schema"] = inline_schema
        elif schema_file:
            normalized_endpoint["expected_json_schema"] = _load_schema_file(schema_file, base_path)

        if not isinstance(normalized_endpoint["headers"], dict):
            raise ValueError(f"{context}.headers must be a mapping.")
        if not isinstance(normalized_endpoint["expected_json_keys"], list):
            raise ValueError(f"{context}.expected_json_keys must be a list.")
        if normalized_endpoint["timeout_ms"] <= 0:
            raise ValueError(f"{context}.timeout_ms must be greater than 0.")

        normalized.append(normalized_endpoint)
    return normalized


def _normalize_grpc_endpoints(endpoints: Any) -> list[dict[str, Any]]:
    if endpoints is None:
        return []
    if not isinstance(endpoints, list):
        raise ValueError("'grpc_endpoints' must be a list.")

    normalized: list[dict[str, Any]] = []
    for index, endpoint in enumerate(endpoints, start=1):
        context = f"grpc_endpoints[{index}]"
        if not isinstance(endpoint, dict):
            raise ValueError(f"{context} must be a mapping.")

        target = _validate_required_string(endpoint, "target", context)
        timeout_ms = int(endpoint.get("timeout_ms", 1500))
        if timeout_ms <= 0:
            raise ValueError(f"{context}.timeout_ms must be greater than 0.")

        normalized.append(
            {
                "name": endpoint.get("name", target),
                "target": target,
                "timeout_ms": timeout_ms,
                "secure": bool(endpoint.get("secure", False)),
            }
        )
    return normalized


def _normalize_thresholds(thresholds: Any) -> dict[str, float]:
    if thresholds is None:
        return deepcopy(DEFAULT_THRESHOLDS)
    if not isinstance(thresholds, dict):
        raise ValueError("'thresholds' must be a mapping.")

    merged = deepcopy(DEFAULT_THRESHOLDS)
    for key, default_value in merged.items():
        merged[key] = float(thresholds.get(key, default_value))
    return merged


def _normalize_logging(logging_config: Any, base_path: Path) -> dict[str, str]:
    if logging_config is None:
        logging_config = {}
    if not isinstance(logging_config, dict):
        raise ValueError("'logging' must be a mapping.")

    merged = deepcopy(DEFAULT_LOGGING)
    merged.update(logging_config)
    return {
        "log_file": _resolve_output_path(base_path, str(merged["log_file"])),
        "alert_file": _resolve_output_path(base_path, str(merged["alert_file"])),
        "report_dir": _resolve_output_path(base_path, str(merged["report_dir"])),
    }


def load_config(path: str = "config.yaml") -> dict[str, Any]:
    """Load configuration from YAML and normalize defaults."""
    config_path = Path(path).resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle) or {}

    if not isinstance(raw_config, dict):
        raise ValueError("Configuration file must contain a YAML object.")

    poll_interval_seconds = int(raw_config.get("poll_interval_seconds", 30))
    max_cycles = int(raw_config.get("max_cycles", 0))
    if poll_interval_seconds <= 0:
        raise ValueError("'poll_interval_seconds' must be greater than 0.")
    if max_cycles < 0:
        raise ValueError("'max_cycles' cannot be negative.")

    base_path = config_path.parent
    system_config = raw_config.get("system", {}) or {}
    if not isinstance(system_config, dict):
        raise ValueError("'system' must be a mapping.")

    disk_path = system_config.get("disk_path", ".")
    if not isinstance(disk_path, str):
        raise ValueError("'system.disk_path' must be a string path.")

    return {
        "poll_interval_seconds": poll_interval_seconds,
        "max_cycles": max_cycles,
        "system": {"disk_path": _resolve_output_path(base_path, disk_path)},
        "api_endpoints": _normalize_api_endpoints(raw_config.get("api_endpoints", []), base_path),
        "grpc_endpoints": _normalize_grpc_endpoints(raw_config.get("grpc_endpoints", [])),
        "thresholds": _normalize_thresholds(raw_config.get("thresholds")),
        "logging": _normalize_logging(raw_config.get("logging"), base_path),
    }
