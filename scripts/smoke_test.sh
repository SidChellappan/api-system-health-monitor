#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"

"${PYTHON_BIN}" -m compileall .
"${PYTHON_BIN}" -m pytest -v
"${PYTHON_BIN}" monitor.py inventory
