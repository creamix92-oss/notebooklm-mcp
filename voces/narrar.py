"""Genera la voz en off de los shorts con Kokoro (ONNX), con cada frase en su segundo exacto.

Uso: python narrar.py <kokoro-v1.0.onnx> <voices-v1.0.bin> <carpeta_salida> [voz ...]
Voces en español de Kokoro: em_alex (hombre), ef_dora (mujer), em_santa.
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL, VOICES, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])
VOCES = sys.argv[4:] or ["em_alex", "ef_dora"]
OUT.mkdir(parents=True, exist_ok=True)

# (segundo de inicio, segundo de fin, texto) — mismos tiempos que guiones_narrados.md
SHORTS = {
    "gibraltar": [
        (0, 6, "Mira bien este mapa. Esto es España… pero en la punta de abajo hay algo que no es España."),
        (6, 13, "Bajamos hasta el Estrecho, donde Europa casi toca África, y el Atlántico se abre al Mediterráneo."),
        (13, 22, "Y ahí está. Gibraltar. Una roca de menos de siete kilómetros cuadrados… con bandera británica."),
        (22, 31, "Todo empezó en mil setecientos cuatro. España estaba en plena guerra por su trono, y una flota inglesa y holandesa aprovechó para tomar el peñón."),
        (31, 40, "Nueve años después, el Tratado de Utrecht lo hizo oficial: Gibraltar pasaba a Gran Bretaña… para siempre."),
        (40, 46, "En mil novecientos sesenta y siete, y en dos mil dos, Gibraltar votó seguir siendo británico."),
        (46, 52, "En mil novecientos sesenta y nueve, España cerró la frontera… hasta el ochenta y cinco."),
        (52, 60, "En julio de dos mil veintiséis, un acuerdo con Europa quitó la verja. Gibraltar sigue siendo británico… pero ya sin verja."),
    ],
    "bolivia": [
        (0, 4, "Este país no tiene ni un metro de costa… y aun así tiene Armada."),
        (4, 12, "Pero no siempre fue así. En mil ochocientos setenta y nueve, Bolivia llegaba hasta el Pacífico, con su propio puerto: Antofagasta."),
        (12, 24, "Ese año estalló la Guerra del Pacífico. Bolivia y Perú, contra Chile. Y Chile ganó."),
        (24, 32, "En mil novecientos cuatro, un tratado lo dejó por escrito: la costa pasaba a Chile. Bolivia se quedaba encerrada entre montañas."),
        (32, 46, "¿Y la Armada? Sus marinos patrullan ríos de la Amazonía… y el lago Titicaca, el lago navegable más alto del mundo, en lo alto de los Andes."),
        (46, 54, "Cada veintitrés de marzo, Bolivia celebra el Día del Mar, y vuelve a reclamar su salida al océano."),
        (54, 60, "En dos mil dieciocho, La Haya falló a favor de Chile. El mar sigue al otro lado."),
    ],
}

kokoro = Kokoro(MODEL, VOICES)
for voz in VOCES:
    for nombre, frases in SHORTS.items():
        sr = 24000
        pista = np.zeros(int(60 * sr), dtype=np.float32)
        for ini, fin, texto in frases:
            hueco = fin - ini - 0.3
            audio, sr = kokoro.create(texto, voice=voz, speed=1.0, lang="es")
            dur = len(audio) / sr
            if dur > hueco:  # si no cabe, se acelera lo justo (sin pasar de 1,2x)
                audio, sr = kokoro.create(texto, voice=voz, speed=min(1.2, dur / hueco * 1.02), lang="es")
                dur = len(audio) / sr
            a = int((ini + 0.15) * sr)
            trozo = audio[: len(pista) - a]
            pista[a : a + len(trozo)] += trozo
            aviso = "  ⚠ no cabe" if dur > hueco else ""
            print(f"{voz} {nombre} {ini:>2}-{fin:<2}s  {dur:4.1f}s{aviso}", flush=True)
        sf.write(OUT / f"{nombre}_{voz}.wav", pista, sr)
print("ok")
