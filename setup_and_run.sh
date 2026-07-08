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
mkdir -p "$ROOT_DIR/simulator"
# ensure a default SQLite DB for local runs
export EVENT_DB="$ROOT_DIR/simulator/events.db"
if [ ! -f "$EVENT_DB" ]; then
	# create empty sqlite file; schema will be created on first append
	touch "$EVENT_DB"
fi

pytest -q

echo "[integration] Running integration runner (using EVENT_DB=$EVENT_DB)"
EVENT_DB="$EVENT_DB" python3 "$ROOT_DIR/tests/run_integration.py"

echo "All steps completed successfully."
