"""Agrupa disparos (hits) en momentos recortables y genera sus títulos."""
from __future__ import annotations

from dataclasses import dataclass, field

from .audio_events import HYPE, SOUND_GROUPS, Hit
from .speech import Word

KIND_WEIGHT = {"palabra": 1.6, "risas": 1.2, "aplausos": 1.1, "ovacion": 1.1, "gritos": 1.1, "hype": 0.8}


@dataclass
class Moment:
    start: float
    end: float
    hits: list[Hit] = field(default_factory=list)

    @property
    def score(self) -> float:
        kinds = {h.kind for h in self.hits}
        base = sum(h.score * KIND_WEIGHT.get(h.kind, 1.0) for h in self.hits)
        return base * (1 + 0.25 * (len(kinds) - 1))  # premia coincidencia de señales

    @property
    def main_kind(self) -> str:
        totals: dict[str, float] = {}
        for h in self.hits:
            totals[h.kind] = totals.get(h.kind, 0) + h.score * KIND_WEIGHT.get(h.kind, 1.0)
        return max(totals, key=totals.get) if totals else "manual"

    @property
    def kinds(self) -> list[str]:
        return sorted({h.kind for h in self.hits})


def build_moments(
    hits: list[Hit], pre: float, post: float, max_len: float, total: float | None = None
) -> list[Moment]:
    """Cada disparo abre una ventana [t-pre, t+post]; las que se solapan se funden."""
    moments: list[Moment] = []
    for h in sorted(hits, key=lambda x: x.t):
        cur = moments[-1] if moments else None
        if cur and h.t <= cur.end and (h.t + post - cur.start) <= max_len:
            cur.end = max(cur.end, h.t + post)
            cur.hits.append(h)
        elif cur and h.t <= cur.end:
            cur.hits.append(h)  # dentro del clip pero ya no cabe alargarlo
        else:
            moments.append(Moment(start=max(0.0, h.t - pre), end=h.t + post, hits=[h]))
    for m in moments:
        if total is not None:
            m.end = min(m.end, total)
        if m.end - m.start > max_len:
            m.end = m.start + max_len
    return [m for m in moments if m.end - m.start >= 2.0]


def emoji_for(kind: str) -> str:
    if kind == "palabra":
        return "🗣️"
    if kind == "hype":
        return HYPE["emoji"]
    if kind in SOUND_GROUPS:
        return SOUND_GROUPS[kind]["emoji"]
    return "🎬"


def label_for(kind: str) -> str:
    if kind == "palabra":
        return "Palabra clave"
    if kind == "hype":
        return HYPE["label"]
    if kind in SOUND_GROUPS:
        return SOUND_GROUPS[kind]["label"]
    return "Clip"


_FALLBACK = {
    "risas": "No pude con la risa",
    "aplausos": "Se ganó los aplausos",
    "ovacion": "El público enloqueció",
    "gritos": "Nadie se lo esperaba",
    "hype": "El momento más intenso",
    "musica": "Momento musical",
    "llanto": "Momento emotivo",
    "explosion": "Explotó todo",
    "manual": "Momento del directo",
}


_DANGLING = set("y e o u de del la el los las un una que en a con por para su sus al se lo mi tu es and the of to a in with for or but is".split())


def _phrase(words: list[Word], t: float, before: float, after: float, max_words: int = 9) -> str:
    """Frase hablada alrededor del instante t, cortada en pausas naturales."""
    sel = [w for w in words if w.end >= t - before and w.start <= t + after]
    if not sel:
        return ""
    # empieza tras la última pausa larga o fin de frase anterior al disparo
    start = 0
    for i in range(1, len(sel)):
        if sel[i].start > t:
            break
        gap = sel[i].start - sel[i - 1].end
        if gap > 0.7 or sel[i - 1].text[-1:] in ".?!":
            start = i
    out: list[str] = []
    for i in range(start, len(sel)):
        out.append(sel[i].text)
        if len(out) >= max_words or (len(out) >= 4 and sel[i].text[-1:] in ".?!"):
            break
    while len(out) > 3 and out[-1].lower().strip(",.;:") in _DANGLING:  # no terminar en "y", "de"…
        out.pop()
    text = " ".join(out).strip(" ,;:-")
    return text[:1].upper() + text[1:] if text else ""


def make_title(moment: Moment, words: list[Word]) -> tuple[str, str]:
    """Devuelve (emoji, título) para el short."""
    kind = moment.main_kind
    emoji = emoji_for(kind)
    kw_hits = [h for h in moment.hits if h.kind == "palabra"]
    anchor = (kw_hits[0] if kw_hits else max(moment.hits, key=lambda h: h.score)) if moment.hits else None
    text = ""
    if anchor and words:
        if anchor.kind == "palabra":
            text = _phrase(words, anchor.t, before=3.0, after=5.0)
        else:  # lo que se dijo justo antes de la risa/aplauso suele ser el remate
            text = _phrase(words, anchor.t - 1.0, before=6.0, after=1.5)
    if not text:
        text = kw_hits[0].text.capitalize() if kw_hits else _FALLBACK.get(kind, _FALLBACK["manual"])
    if len(text) > 70:
        text = text[:67].rsplit(" ", 1)[0] + "…"
    return emoji, text
