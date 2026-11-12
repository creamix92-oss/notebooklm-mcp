#!/usr/bin/env bash
# ClipRadar – arranque en Linux / macOS
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
if [ ! -d .venv ]; then
  echo "Preparando ClipRadar por primera vez (tarda unos minutos)…"
  "$PY" -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python -m app
