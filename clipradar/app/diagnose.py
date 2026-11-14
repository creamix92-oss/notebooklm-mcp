"""Autodiagnóstico: prueba cada pieza de ClipRadar y escribe un informe.

Uso:  python -m app.diagnose   ->  genera diagnostico.txt
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

from .config import DATA_DIR, ROOT

REPORT = ROOT / "diagnostico.txt"
VOD_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # video público de 19 s
LIVE_URL = "https://www.youtube.com/watch?v=jfKfPfyJRdk"  # radio 24/7
lines: list[str] = []
results: list[tuple[str, bool]] = []


def out(msg: str = "") -> None:
    print(msg, flush=True)
    lines.append(msg)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def step(name: str):
    def deco(fn):
        out(f"\n=== {name} ===")
        t = time.time()
        try:
            fn()
            ok = True
            out(f"[OK] {name} ({time.time() - t:.0f} s)")
        except Exception:
            ok = False
            out(f"[FALLO] {name}\n{traceback.format_exc()[-1800:]}")
        results.append((name, ok))
        return fn

    return deco


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # la consola de Windows no admite emojis
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass
    work = DATA_DIR / "diagnostico"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    synth = work / "prueba.mp4"
    out(f"ClipRadar diagnostico  {time.strftime('%Y-%m-%d %H:%M')}")
    out(f"Sistema: {platform.platform()}  Python {sys.version.split()[0]} ({platform.architecture()[0]})")
    out(f"Carpeta: {ROOT}")
    for tool in ("node", "deno", "ffmpeg"):
        out(f"{tool} en PATH: {shutil.which(tool) or 'no'}")

    @step("1. ffmpeg")
    def _():
        from . import ff

        exe = ff.ffmpeg_bin()
        ver = subprocess.run([exe, "-version"], capture_output=True).stdout.decode("utf-8", "replace").splitlines()[0]
        out(f"{exe}\n{ver}")
        ff.run(["-f", "lavfi", "-i", "testsrc2=s=1280x720:r=30:d=40", "-f", "lavfi", "-i", "anoisesrc=d=40:c=pink:a=0.02",
                "-f", "lavfi", "-i", "anoisesrc=d=40:c=white:a=0.9", "-filter_complex",
                "[2:a]volume='if(between(t,20,23),1,0)':eval=frame[b];[1:a][b]amix=inputs=2:normalize=0[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", str(synth)])
        out(f"video de prueba: {synth.stat().st_size // 1024} KB  {ff.probe(synth)}")

    @step("2. Deteccion de picos + render vertical con titulo, emoji y subtitulos")
    def _():
        from . import ff
        from .audio_events import detect_hype
        from .render import _emoji_font_path, _text_font_path, render_clip
        from .speech import Word

        hits = detect_hype(ff.read_audio(synth))
        out(f"picos: {[round(h.t, 1) for h in hits]}")
        assert hits, "no se detecto el pico de volumen"
        out(f"fuente texto: {_text_font_path()}  fuente emoji: {_emoji_font_path()}")
        dest = work / "clip.mp4"
        render_clip(synth, 14, 26, dest, emoji="🔥", title="Prueba de título", captions=True,
                    words=[Word(15, 16, "hola"), Word(16, 17, "mundo")])
        out(f"clip: {dest.stat().st_size // 1024} KB  {ff.probe(dest)}")

    @step("3. Modelo de sonidos (YAMNet)")
    def _():
        from . import ff
        from .audio_events import detect_sounds, yamnet_status

        found = detect_sounds(ff.read_audio(synth), ["risas", "aplausos"])
        out(f"estado: {yamnet_status()}  eventos: {None if found is None else len(found)}")
        assert found is not None, yamnet_status()["reason"]

    @step("4. Modelo de voz (Whisper tiny)")
    def _():
        from . import ff
        from .speech import transcribe

        out(f"palabras: {len(transcribe(ff.read_audio(synth, 0, 10), 'tiny', 'es'))}")

    @step("5. yt-dlp: version")
    def _():
        import yt_dlp

        out(f"yt-dlp {yt_dlp.version.__version__}")

    def run_job(url: str, mode: str, seconds: float | None = None):
        from .jobs import Job, clean_settings

        job = Job(url, mode, clean_settings({"sounds": ["risas", "aplausos", "musica"], "hype": True, "sensitivity": 0.8,
                                             "whisper_model": "tiny", "max_clips": 2, "pre": 4, "post": 6, "quality": 480}))
        th = threading.Thread(target=job.run, daemon=True)
        th.start()
        if seconds:
            th.join(seconds)
            job.stop()
        th.join(300)
        out(f"estado: {job.status} | {job.message}")
        out("registro:\n  " + "\n  ".join(job.log[-25:]))
        cap = job.dir / "capture.log"
        if cap.exists():
            out("capture.log:\n  " + "\n  ".join(cap.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]))
        out(f"duracion grabada/analizada: {job.duration:.0f} s  clips: {len(job.clips)}  disparos: {len(job.hits)}")
        return job

    @step("6. Video de YouTube completo (descarga + analisis + clips)")
    def _():
        job = run_job(VOD_URL, "vod")
        assert job.status == "done", job.message

    @step("7. Directo de YouTube (60 s de grabacion)")
    def _():
        job = run_job(LIVE_URL, "live", 60)
        assert job.status in ("done", "stopped") and job.duration > 10, job.message

    out("\n=== RESUMEN ===")
    for name, ok in results:
        out(f"{'OK   ' if ok else 'FALLO'} {name}")
    out(f"\nInforme guardado en: {REPORT}")


if __name__ == "__main__":
    main()
