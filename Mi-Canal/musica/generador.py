#!/usr/bin/env python3
"""Generador de instrumentales (oración / alabanza) -> MIDI multipista + vista previa WAV.

Solo biblioteca estándar para el MIDI; numpy opcional para la vista previa.
Uso:
  python generador.py --estilo oracion --tonalidad D --seed 7 --salida oracion_D.mid --preview oracion_D.wav
El MIDI es original (generado por reglas y azar con semilla), listo para cargarlo
en REAPER u otro DAW y asignar instrumentos de calidad a cada pista.
"""
import argparse, random, struct, wave

PPQ = 480
ESCALA = [0, 2, 4, 5, 7, 9, 11]  # mayor
RAICES = {"C": 48, "D": 50, "E": 52, "F": 53, "G": 55, "A": 57, "B": 59}
ESTILOS = {
    "oracion":  dict(bpm=68, prog=[0, 4, 5, 3], melodia=0.65, bateria="minima"),
    "alabanza": dict(bpm=82, prog=[0, 4, 5, 3], melodia=0.85, bateria="suave"),
}
# (nombre, compases, capas)
ESTRUCTURA = [("intro", 4, {"pad"}), ("estrofa", 8, {"pad", "bajo", "bat"}),
              ("coro", 8, {"pad", "bajo", "bat", "mel"}), ("estrofa2", 8, {"pad", "bajo", "bat", "mel"}),
              ("coro2", 8, {"pad", "bajo", "bat", "mel"}), ("final", 4, {"pad"})]
RITMOS = [[(0, 2), (2, 1), (3, 1)], [(0, 1.5), (1.5, .5), (2, 2)], [(0, 4)],
          [(1, 1), (2, 1), (3, 1)], [(0, 1), (1, 1), (2, 2)], [(0.5, 1.5), (2, 1), (3, 1)]]


def nota(raiz, grado):
    return raiz + ESCALA[grado % 7] + 12 * (grado // 7)


def vlq(n):
    b = [n & 0x7F]
    n >>= 7
    while n:
        b.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(b))


def pista(eventos, nombre, canal=None, programa=None):
    """eventos: (tick, orden, bytes). Devuelve bloque MTrk."""
    ev = [(0, -2, b"\xff\x03" + bytes([len(nombre)]) + nombre.encode())]
    if canal is not None and programa is not None:
        ev.append((0, -1, bytes([0xC0 | canal, programa])))
    ev += eventos
    ev.sort(key=lambda e: (e[0], e[1]))
    data, t = b"", 0
    for tick, _, msg in ev:
        data += vlq(tick - t) + msg
        t = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def on_off(notas, canal):
    ev = []
    for ini, dur, p, vel in notas:
        t0, t1 = int(ini * PPQ), int((ini + dur) * PPQ)
        ev.append((t0, 1, bytes([0x90 | canal, p, vel])))
        ev.append((max(t1, t0 + 1), 0, bytes([0x80 | canal, p, 0])))
    return ev


def componer(estilo, tonalidad, seed):
    cfg, rnd, raiz = ESTILOS[estilo], random.Random(seed), RAICES[tonalidad]
    prog = cfg["prog"]
    pad, bajo, mel, bat = [], [], [], []
    beat, grado_mel = 0.0, 11
    for nombre, compases, capas in ESTRUCTURA:
        for c in range(compases):
            d = prog[c % 4]
            acorde = [nota(raiz, 7 + d + k) for k in (0, 2, 4)]
            if "pad" in capas:
                for p in acorde:
                    pad.append((beat, 4, p, 62 if nombre in ("intro", "final") else 72))
            if "bajo" in capas:
                bajo.append((beat, 2.5, nota(raiz, d - 7), 88))
                bajo.append((beat + 2, 1.5 if estilo == "oracion" else 0.75, nota(raiz, d - 7 + (4 if estilo == "alabanza" else 0)), 74))
            if "bat" in capas:
                for b in range(8):
                    bat.append((beat + b / 2, 0.25, 70, 36 if b % 2 else 52))  # maracas suaves
                if estilo == "alabanza":
                    bat.append((beat, 0.25, 36, 84)); bat.append((beat + 2, 0.25, 36, 78))
                    bat.append((beat + 1, 0.25, 37, 60)); bat.append((beat + 3, 0.25, 37, 64))
            if "mel" in capas and rnd.random() < cfg["melodia"] + 0.15:
                ultimo = c == compases - 1
                ritmo = [(0, 4)] if ultimo else rnd.choice(RITMOS)
                tonos = {(d + k) % 7 for k in (0, 2, 4)}
                for i, (ini, dur) in enumerate(ritmo):
                    cand = [g for g in range(9, 16) if g % 7 in tonos]
                    if i == 0 or rnd.random() < 0.4:
                        grado_mel = min(cand, key=lambda g: abs(g - grado_mel) + rnd.random())
                    else:
                        grado_mel = max(9, min(15, grado_mel + rnd.choice((-1, 1))))
                    if ultimo:
                        grado_mel = min((g for g in range(9, 16) if g % 7 == d % 7), key=lambda g: abs(g - grado_mel))
                    mel.append((beat + ini, dur * 0.95, nota(raiz, grado_mel), 80 + rnd.randint(-6, 6)))
            beat += 4
    return cfg["bpm"], pad, bajo, mel, bat, beat


def escribir_midi(ruta, bpm, pad, bajo, mel, bat):
    tempo = int(60_000_000 / bpm)
    t0 = pista([(0, -1, b"\xff\x51\x03" + tempo.to_bytes(3, "big")), (0, -1, b"\xff\x58\x04\x04\x02\x18\x08")], "Tempo")
    pistas = [t0,
              pista(on_off(pad, 0), "Pad", 0, 89),
              pista(on_off(bajo, 1), "Bajo", 1, 33),
              pista(on_off(mel, 2), "Melodia", 2, 0),
              pista(on_off([(i, d, p, v) for i, d, p, v in
                            ((a, b, c, e) for a, b, e, c in bat)], 9), "Bateria")]
    with open(ruta, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 1, len(pistas), PPQ))
        for p in pistas:
            f.write(p)


def vista_previa(ruta, bpm, pad, bajo, mel, bat, beats):
    import numpy as np
    sr, spb = 22050, 60.0 / bpm
    out = np.zeros(int((beats * spb + 2) * sr))

    def tono(p, dur, vel, forma):
        n = int((dur * spb + 0.3) * sr)
        t = np.arange(n) / sr
        f = 440 * 2 ** ((p - 69) / 12)
        if forma == "pad":
            y = np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.003 * t)
            env = np.minimum(t / .4, 1) * np.exp(-np.maximum(t - dur * spb, 0) * 6)
        elif forma == "bajo":
            y = np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t)
            env = np.minimum(t / .02, 1) * np.exp(-t * 2.2)
        else:
            y = np.sign(np.sin(2 * np.pi * f * t)) * .15 + np.sin(2 * np.pi * f * t)
            env = np.minimum(t / .03, 1) * np.exp(-np.maximum(t - dur * spb, 0) * 9) * np.exp(-t * .8)
        return y * env * vel / 127 * .18

    for capa, forma in ((pad, "pad"), (bajo, "bajo"), (mel, "mel")):
        for ini, dur, p, vel in capa:
            y, i0 = tono(p, dur, vel, forma), int(ini * spb * sr)
            out[i0:i0 + len(y)] += y[:len(out) - i0]
    rnd = np.random.default_rng(1)
    for ini, dur, p, vel in [(a, b, c, e) for a, b, e, c in bat]:
        i0, n = int(ini * spb * sr), int(.08 * sr)
        ruido = rnd.standard_normal(n) * np.exp(-np.arange(n) / (.02 * sr)) * (.5 if p == 70 else .9)
        if p == 36:
            ruido = np.sin(2 * np.pi * 55 * np.arange(n) / sr) * np.exp(-np.arange(n) / (.03 * sr))
        out[i0:i0 + n] += ruido[:len(out) - i0] * vel / 127 * .12
    out = out / max(1e-9, np.abs(out).max()) * .85
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--estilo", choices=ESTILOS, default="oracion")
    ap.add_argument("--tonalidad", choices=RAICES, default="D")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--salida", default="instrumental.mid")
    ap.add_argument("--preview", help="ruta .wav de vista previa (requiere numpy)")
    a = ap.parse_args()
    bpm, pad, bajo, mel, bat, beats = componer(a.estilo, a.tonalidad, a.seed)
    escribir_midi(a.salida, bpm, pad, bajo, mel, bat)
    print(f"{a.salida}: {bpm} bpm, {int(beats // 4)} compases, {len(mel)} notas de melodía")
    if a.preview:
        vista_previa(a.preview, bpm, pad, bajo, mel, bat, beats)
        print("vista previa:", a.preview)
