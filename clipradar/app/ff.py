"""Utilidades de ffmpeg: localizar el binario, medir duración y extraer audio."""
from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

from .config import SAMPLE_RATE


@lru_cache(maxsize=1)
def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:  # binario empaquetado por pip (útil en Windows sin ffmpeg instalado)
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "No se encontró ffmpeg. Instálalo o ejecuta: pip install imageio-ffmpeg"
        ) from exc


def run(args: list[str], cwd: Path | None = None, timeout: float | None = None) -> str:
    """Ejecuta ffmpeg y devuelve stderr; lanza RuntimeError si falla."""
    cmd = [ffmpeg_bin(), "-hide_banner", "-nostdin", "-y", *args]
    p = subprocess.run(cmd, capture_output=True, cwd=cwd, timeout=timeout)
    err = p.stderr.decode("utf-8", "replace")
    if p.returncode != 0:
        raise RuntimeError("ffmpeg falló:\n" + err[-1500:])
    return err


_DUR = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_VID = re.compile(r"Stream #.*Video:.*?(\d{2,5})x(\d{2,5})")


def probe(path: Path | str) -> dict:
    """Duración y tamaño del video sin depender de ffprobe."""
    p = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-nostdin", "-i", str(path)],
        capture_output=True,
    )
    err = p.stderr.decode("utf-8", "replace")
    info: dict = {"duration": 0.0, "width": 0, "height": 0, "has_video": False}
    m = _DUR.search(err)
    if m:
        h, mi, s = m.groups()
        info["duration"] = int(h) * 3600 + int(mi) * 60 + float(s)
    v = _VID.search(err)
    if v:
        info.update(width=int(v.group(1)), height=int(v.group(2)), has_video=True)
    info["has_audio"] = "Audio:" in err
    return info


def read_audio(path: Path | str, start: float = 0.0, duration: float | None = None) -> np.ndarray:
    """Decodifica a PCM mono 16 kHz float32 en [-1, 1]."""
    args = [ffmpeg_bin(), "-hide_banner", "-nostdin", "-loglevel", "error"]
    if start > 0:
        args += ["-ss", f"{start:.3f}"]
    args += ["-i", str(path)]
    if duration is not None:
        args += ["-t", f"{duration:.3f}"]
    args += ["-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "-"]
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0 and not p.stdout:
        raise RuntimeError("No se pudo leer el audio:\n" + p.stderr.decode("utf-8", "replace")[-800:])
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
