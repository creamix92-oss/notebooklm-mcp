"""Detección de eventos de sonido: risas, aplausos, gritos, ovaciones, música…

Dos motores:
  * YAMNet (ONNX, 521 clases de AudioSet) – reconoce el *tipo* de sonido.
  * Detector de energía propio ("hype") – picos de volumen respecto al fondo;
    no necesita ningún modelo y siempre está disponible.
"""
from __future__ import annotations

import csv
import threading
import urllib.request
from dataclasses import dataclass

import numpy as np

from .config import MODELS_DIR, SAMPLE_RATE, YAMNET_PATH, YAMNET_URL

# Grupos de disparadores -> nombres de clase de AudioSet (YAMNet).
SOUND_GROUPS: dict[str, dict] = {
    "risas": {
        "emoji": "😂",
        "label": "Risas",
        "classes": ["Laughter", "Baby laughter", "Giggle", "Snicker", "Belly laugh", "Chuckle, chortle"],
    },
    "aplausos": {"emoji": "👏", "label": "Aplausos", "classes": ["Applause", "Clapping"]},
    "ovacion": {
        "emoji": "🙌",
        "label": "Ovación / público",
        "classes": ["Cheering", "Crowd", "Whoop", "Chant", "Hubbub, speech noise, speech babble"],
    },
    "gritos": {
        "emoji": "😱",
        "label": "Gritos",
        "classes": ["Screaming", "Shout", "Yell", "Bellow", "Children shouting", "Battle cry"],
    },
    "musica": {"emoji": "🎵", "label": "Música / canto", "classes": ["Music", "Singing"]},
    "llanto": {"emoji": "😭", "label": "Llanto", "classes": ["Crying, sobbing", "Wail, moan", "Whimper"]},
    "explosion": {
        "emoji": "💥",
        "label": "Explosión / disparos",
        "classes": ["Explosion", "Gunshot, gunfire", "Machine gun", "Boom", "Fireworks"],
    },
}
HYPE = {"emoji": "🔥", "label": "Pico de volumen"}

# Lista embebida de las 521 clases por si no existe el CSV (se rellena al cargar).
_CLASS_NAMES: list[str] | None = None


@dataclass
class Hit:
    t: float  # segundo (relativo al audio analizado)
    kind: str  # "risas", "hype", "palabra"…
    score: float  # 0..1
    text: str = ""

    def asdict(self) -> dict:
        return {"t": round(self.t, 2), "kind": self.kind, "score": round(float(self.score), 3), "text": self.text}


# ----------------------------------------------------------------- energía
def rms_envelope(audio: np.ndarray, hop_s: float = 0.25) -> np.ndarray:
    hop = int(SAMPLE_RATE * hop_s)
    n = len(audio) // hop
    if n == 0:
        return np.zeros(0, dtype=np.float32)
    frames = audio[: n * hop].reshape(n, hop)
    return np.sqrt((frames**2).mean(axis=1) + 1e-12)


def detect_hype(audio: np.ndarray, sensitivity: float = 0.5, hop_s: float = 0.25) -> list[Hit]:
    """Picos de volumen muy por encima del nivel de fondo reciente.

    `sensitivity` 0..1: más alto = dispara con picos más pequeños.
    """
    env = rms_envelope(audio, hop_s)
    if len(env) < 8:
        return []
    db = 20 * np.log10(env + 1e-6)
    # fondo = mediana móvil de los últimos ~30 s
    win = max(8, int(30 / hop_s))
    pad = np.concatenate([np.full(win, np.median(db[:win])), db])
    bg = np.array([np.median(pad[i : i + win]) for i in range(len(db))])
    spread = max(3.0, float(np.percentile(db, 90) - np.percentile(db, 50)))
    thr_db = 14.0 - 9.0 * float(np.clip(sensitivity, 0, 1))  # 14 dB .. 5 dB sobre el fondo
    excess = db - bg
    above = (excess > thr_db) & (db > -45)
    hits: list[Hit] = []
    i = 0
    while i < len(above):
        if above[i]:
            j = i
            while j < len(above) and above[j]:
                j += 1
            if (j - i) * hop_s >= 0.5:  # mínimo medio segundo sostenido
                peak = i + int(np.argmax(excess[i:j]))
                score = float(np.clip(excess[peak] / (thr_db + spread + 6), 0.3, 1.0))
                hits.append(Hit(t=i * hop_s, kind="hype", score=score))
            i = j
        else:
            i += 1
    return hits


# ------------------------------------------------------------------ YAMNet
_lock = threading.Lock()
_session = None
_unavailable_reason: str | None = None


def _class_names() -> list[str]:
    global _CLASS_NAMES
    if _CLASS_NAMES is None:
        path = MODELS_DIR / "yamnet_class_map.csv"
        if not path.exists():
            urllib.request.urlretrieve(YAMNET_URL.rsplit("/", 1)[0] + "/yamnet_class_map.csv", path)
        with open(path, newline="", encoding="utf-8") as f:
            _CLASS_NAMES = [row["display_name"] for row in csv.DictReader(f)]
    return _CLASS_NAMES


def yamnet_status() -> dict:
    return {"available": _unavailable_reason is None, "loaded": _session is not None, "reason": _unavailable_reason}


def _load():
    """Carga (y descarga la primera vez) el modelo. Devuelve None si no se puede."""
    global _session, _unavailable_reason
    with _lock:
        if _session is not None or _unavailable_reason:
            return _session
        try:
            import onnxruntime as ort

            if not YAMNET_PATH.exists():
                tmp = YAMNET_PATH.with_suffix(".part")
                urllib.request.urlretrieve(YAMNET_URL, tmp)
                tmp.replace(YAMNET_PATH)
            _class_names()
            opts = ort.SessionOptions()
            opts.log_severity_level = 3
            _session = ort.InferenceSession(str(YAMNET_PATH), opts, providers=["CPUExecutionProvider"])
        except Exception as exc:
            _unavailable_reason = f"{type(exc).__name__}: {exc}"
            _session = None
        return _session


def _mel_filterbank(n_fft_bins: int, n_mels: int = 64, fmin: float = 125.0, fmax: float = 7500.0) -> np.ndarray:
    def hz2mel(f):
        return 1127.0 * np.log(1.0 + np.asarray(f) / 700.0)

    freqs = np.linspace(0, SAMPLE_RATE / 2, n_fft_bins)
    mel = hz2mel(freqs)
    edges = np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2)
    fb = np.zeros((n_fft_bins, n_mels), dtype=np.float32)
    for i in range(n_mels):
        lo, ce, hi = edges[i], edges[i + 1], edges[i + 2]
        fb[:, i] = np.maximum(0, np.minimum((mel - lo) / (ce - lo), (hi - mel) / (hi - ce)))
    fb[0, :] = 0
    return fb


def _log_mel_patches(audio: np.ndarray) -> np.ndarray:
    """Características de YAMNet: log-mel 64 bandas, parches de 0.96 s cada 0.48 s."""
    win, hop, nfft = 400, 160, 512
    if len(audio) < win:
        audio = np.pad(audio, (0, win - len(audio)))
    n = 1 + (len(audio) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    frames = audio[idx] * np.hanning(win + 1)[:-1].astype(np.float32)
    mag = np.abs(np.fft.rfft(frames, nfft)).astype(np.float32)
    mel = np.log(mag @ _mel_filterbank(nfft // 2 + 1) + 0.001)
    if len(mel) < 96:
        mel = np.pad(mel, ((0, 96 - len(mel)), (0, 0)), constant_values=np.log(0.001))
    starts = range(0, len(mel) - 96 + 1, 48)
    return np.stack([mel[s : s + 96] for s in starts]).astype(np.float32)


def _scores(audio: np.ndarray) -> np.ndarray | None:
    """Matriz [frames(0.48 s), 521] de probabilidades, o None si no hay modelo."""
    sess = _load()
    if sess is None:
        return None
    inp = sess.get_inputs()[0]
    rank = len(inp.shape)
    if rank <= 1:  # el modelo recibe la onda directamente
        outs = sess.run(None, {inp.name: audio.astype(np.float32)})
    else:  # el modelo recibe parches log-mel
        patches = _log_mel_patches(audio)
        shape = [d if isinstance(d, int) else None for d in inp.shape]
        if rank == 4:
            patches = patches[:, None, :, :] if shape[1] == 1 else patches[..., None]
        if shape[0] == 1:  # lote fijo de 1
            outs_list = [sess.run(None, {inp.name: p[None]}) for p in patches]
            outs = [np.concatenate([o[k] for o in outs_list]) for k in range(len(outs_list[0]))]
        else:
            outs = sess.run(None, {inp.name: patches})
    for o in outs:
        if o.ndim == 2 and o.shape[-1] == 521:
            return o
    raise RuntimeError("El modelo YAMNet no devolvió puntuaciones de 521 clases")


def detect_sounds(audio: np.ndarray, groups: list[str], sensitivity: float = 0.5) -> list[Hit] | None:
    """Devuelve los eventos de los grupos pedidos; None si YAMNet no está disponible."""
    groups = [g for g in groups if g in SOUND_GROUPS]
    if not groups or len(audio) < SAMPLE_RATE // 2:
        return []
    scores = _scores(audio)
    if scores is None:
        return None
    names = _class_names()
    frame_s = len(audio) / SAMPLE_RATE / max(1, len(scores))
    frame_s = min(frame_s, 0.48) if len(scores) > 1 else 0.48
    thr = 0.50 - 0.42 * float(np.clip(sensitivity, 0, 1))  # 0.50 .. 0.08
    hits: list[Hit] = []
    for g in groups:
        idx = [names.index(c) for c in SOUND_GROUPS[g]["classes"] if c in names]
        if not idx:
            continue
        s = np.minimum(1.0, scores[:, idx].sum(axis=1))  # suma de las clases afines
        if len(s) >= 3:  # suavizado: atenúa disparos de un solo frame
            s = np.convolve(s, [0.25, 0.5, 0.25], mode="same")
        above = s > thr
        i = 0
        while i < len(above):
            if above[i]:
                j = i
                while j < len(above) and above[j]:
                    j += 1
                peak = i + int(np.argmax(s[i:j]))
                hits.append(Hit(t=peak * frame_s + 0.48, kind=g, score=float(min(1.0, s[peak]))))
                i = j
            else:
                i += 1
    return hits
