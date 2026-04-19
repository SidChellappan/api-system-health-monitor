#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"
CONFIG_PATH="${1:-config.yaml}"
CYCLES="${CYCLES:-1}"

echo "Installing dependencies..."
"${PYTHON_BIN}" -m pip install -r requirements.txt

echo "Running tests..."
"${PYTHON_BIN}" -m pytest -v

echo "Running monitor..."
"${PYTHON_BIN}" monitor.py --config "${CONFIG_PATH}" run --cycles "${CYCLES}" --report
