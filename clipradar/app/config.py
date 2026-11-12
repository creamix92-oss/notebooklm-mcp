"""Rutas y ajustes globales de ClipRadar."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("CLIPRADAR_DATA", ROOT / "data")).resolve()
JOBS_DIR = DATA_DIR / "jobs"
MODELS_DIR = DATA_DIR / "models"
WEB_DIR = ROOT / "web"

HOST = os.environ.get("CLIPRADAR_HOST", "127.0.0.1")
PORT = int(os.environ.get("CLIPRADAR_PORT", "8787"))

# Modelo de eventos de sonido (YAMNet, AudioSet, Apache-2.0) en formato ONNX.
YAMNET_URL = os.environ.get(
    "CLIPRADAR_YAMNET_URL",
    "https://huggingface.co/zeropointnine/yamnet-onnx/resolve/main/yamnet.onnx",
)
YAMNET_PATH = MODELS_DIR / "yamnet.onnx"

SAMPLE_RATE = 16000

for d in (DATA_DIR, JOBS_DIR, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)
