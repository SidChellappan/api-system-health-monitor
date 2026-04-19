from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from config_loader import load_config


def test_load_config_normalizes_paths_and_schema_files() -> None:
    tmp_path = Path.cwd() / "tests_runtime" / f"config_loader_{uuid4().hex}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("type: object\nrequired:\n  - id\n", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "poll_interval_seconds: 5",
                "system:",
                "  disk_path: .",
                "api_endpoints:",
                "  - name: Example",
                "    url: https://example.com",
                f"    schema_file: {schema_path.name}",
                "logging:",
                "  log_file: logs/test.ndjson",
                "  alert_file: logs/alerts.log",
                "  report_dir: reports",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config["logging"]["log_file"].endswith("logs\\test.ndjson") or config["logging"]["log_file"].endswith("logs/test.ndjson")
    assert config["api_endpoints"][0]["expected_json_schema"]["required"] == ["id"]
