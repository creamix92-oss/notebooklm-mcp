"""Transcripción (faster-whisper) y búsqueda de palabras/frases clave."""
from __future__ import annotations

import re
import threading
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

import numpy as np

from .audio_events import Hit
from .config import MODELS_DIR

_lock = threading.Lock()
_models: dict[str, object] = {}
_error: str | None = None


@dataclass
class Word:
    start: float
    end: float
    text: str

    def asdict(self) -> dict:
        return {"s": round(self.start, 2), "e": round(self.end, 2), "w": self.text}


def whisper_status() -> dict:
    return {"available": _error is None, "loaded": list(_models), "reason": _error}


def _model(size: str):
    global _error
    with _lock:
        if size in _models:
            return _models[size]
        try:
            from faster_whisper import WhisperModel

            m = WhisperModel(size, device="auto", compute_type="auto", download_root=str(MODELS_DIR / "whisper"))
        except Exception as first:
            try:
                from faster_whisper import WhisperModel

                m = WhisperModel(size, device="cpu", compute_type="int8", download_root=str(MODELS_DIR / "whisper"))
            except Exception as exc:
                _error = f"{type(exc).__name__}: {exc}"
                raise RuntimeError(
                    "No se pudo cargar Whisper (¿sin internet para descargar el modelo?): " + _error
                ) from first
        _models[size] = m
        _error = None
        return m


def transcribe(audio: np.ndarray, model_size: str = "small", language: str | None = None, offset: float = 0.0) -> list[Word]:
    """Palabras con marca de tiempo (segundos + offset)."""
    if len(audio) < 1600:
        return []
    model = _model(model_size)
    segments, _info = model.transcribe(
        audio,
        language=language or None,
        word_timestamps=True,
        vad_filter=True,
        beam_size=1,
        condition_on_previous_text=False,
    )
    words: list[Word] = []
    for seg in segments:
        for w in seg.words or []:
            txt = w.word.strip()
            if txt:
                words.append(Word(w.start + offset, w.end + offset, txt))
    return words


def normalize(text: str) -> str:
    """minúsculas, sin acentos ni signos: '¡Qué GOLAZO, niño!' -> 'que golazo nino'."""
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def _tokens(text: str) -> list[str]:
    return [t for t in normalize(text).split() if t]


def find_keywords(words: list[Word], keywords: list[str], fuzzy: float = 0.84) -> list[Hit]:
    """Busca cada palabra o frase clave en la transcripción (tolerante a errores)."""
    toks: list[tuple[str, Word]] = []
    for w in words:
        for t in _tokens(w.text):
            toks.append((t, w))
    hits: list[Hit] = []
    for kw in keywords:
        kt = _tokens(kw)
        if not kt:
            continue
        n = len(kt)
        target = " ".join(kt)
        last_t = -999.0
        for i in range(0, len(toks) - n + 1):
            cand = " ".join(t for t, _ in toks[i : i + n])
            if cand == target:
                score = 1.0
            else:
                if abs(len(cand) - len(target)) > 3 or len(target) < 4:
                    continue
                score = SequenceMatcher(None, cand, target).ratio()
                if score < fuzzy:
                    continue
            t0 = toks[i][1].start
            if t0 - last_t < 2.0:  # misma mención
                continue
            last_t = t0
            hits.append(Hit(t=t0, kind="palabra", score=float(score), text=kw.strip()))
    return hits


def text_between(words: list[Word], start: float, end: float) -> str:
    return " ".join(w.text for w in words if w.end > start and w.start < end).strip()
