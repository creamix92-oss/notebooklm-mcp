"""Genera la narración frase a frase y guarda el tiempo exacto de cada frase y de cada escena.

Uso: python narrar.py <kokoro-v1.0.onnx> <voices-v1.0.bin> <carpeta_salida>
Salida: narracion.wav y tiempos.json: {"escenas": [{"inicio", "fin", "frases": [[ini, fin], ...]}], "total"}.
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
VOZ, SPEED, SR = "em_alex", 1.12, 24000
GAP_FRASE, GAP_ESCENA, INICIO = 0.22, 0.45, 0.05

kokoro = Kokoro(MODEL, VOICES)
pistas, escenas, t = [np.zeros(int(INICIO * SR), np.float32)], [], INICIO
for i, sc in enumerate(SCENES):
    ini_escena, frases = t, []
    for j, fr in enumerate(sc["frases"]):
        audio, sr = kokoro.create(fr["texto"], voice=VOZ, speed=SPEED, lang="es")
        assert sr == SR
        audio = audio.astype(np.float32)
        gap = GAP_ESCENA if j == len(sc["frases"]) - 1 else GAP_FRASE
        pistas += [audio, np.zeros(int(gap * SR), np.float32)]
        frases.append([round(t, 3), round(t + len(audio) / SR + gap, 3)])
        t += len(audio) / SR + gap
    escenas.append(dict(inicio=round(ini_escena, 3), fin=round(t, 3), frases=frases))
    print(f"{i:2d}  {ini_escena:6.1f}s  +{t - ini_escena:5.1f}s  {sc['titulo']}", flush=True)
pistas.append(np.zeros(int(1.2 * SR), np.float32))
pista = np.concatenate(pistas)
sf.write(OUT / "narracion.wav", pista, SR)
(OUT / "tiempos.json").write_text(json.dumps(dict(escenas=escenas, total=round(len(pista) / SR, 3))))
print(f"total {len(pista) / SR:.1f}s")
