"""Genera la narración del short de Trujillo (una pista por escena) y guarda la duración de cada escena.

Uso: python narrar.py <kokoro-v1.0.onnx> <voices-v1.0.bin> <carpeta_salida>
Salida: narracion.wav y tiempos.json (inicio y fin de cada escena, en segundos).
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escenas import SCENES  # noqa: E402

MODEL, VOICES, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
VOZ, SPEED, SR = "em_alex", 1.1, 24000
ENTRADA, SALIDA = 0.35, 0.55  # silencio antes y después de cada frase

kokoro = Kokoro(MODEL, VOICES)
trozos, tiempos, t = [], [], 0.0
for i, sc in enumerate(SCENES):
    audio, sr = kokoro.create(sc["voz"], voice=VOZ, speed=SPEED, lang="es")
    assert sr == SR
    dur = ENTRADA + len(audio) / SR + SALIDA
    trozos += [np.zeros(int(ENTRADA * SR), np.float32), audio.astype(np.float32),
               np.zeros(int(SALIDA * SR), np.float32)]
    tiempos.append([round(t, 3), round(t + dur, 3)])
    print(f"{i:2d}  {t:6.1f}s  +{dur:4.1f}s  {sc['titulo']}", flush=True)
    t += dur
pista = np.concatenate(trozos + [np.zeros(int(1.0 * SR), np.float32)])
tiempos[-1][1] = round(len(pista) / SR, 3)
sf.write(OUT / "narracion.wav", pista, SR)
(OUT / "tiempos.json").write_text(json.dumps(tiempos))
print(f"total {len(pista) / SR:.1f}s")
