#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "[setup] Creating virtual environment at $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "[setup] Upgrading pip and installing requirements"
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

echo "[test] Running unit tests with pytest"
pytest -q

echo "[integration] Running integration runner"
python3 "$ROOT_DIR/tests/run_integration.py"

echo "All steps completed successfully."
