"""Motor de trabajos: descarga/captura, análisis, y generación de shorts."""
from __future__ import annotations

import csv
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path

import numpy as np

from . import ff
from .audio_events import SOUND_GROUPS, Hit, detect_hype, detect_sounds, yamnet_status
from .config import JOBS_DIR, SAMPLE_RATE
from .moments import Moment, build_moments, make_title
from .render import render_clip
from .speech import Word, find_keywords, transcribe

DEFAULTS = {
    "keywords": [],  # palabras, frases o nombres
    "sounds": ["risas", "aplausos"],  # grupos de SOUND_GROUPS
    "hype": True,  # picos de volumen
    "sensitivity": 0.5,
    "pre": 8.0,  # segundos antes del disparo
    "post": 12.0,  # segundos después
    "max_len": 59.0,
    "max_clips": 12,  # solo VOD: se quedan los mejores
    "layout": "vertical_blur",  # vertical_blur | vertical_crop | original
    "show_title": True,
    "captions": True,
    "smart_titles": True,  # transcribir el clip para titularlo
    "language": "es",  # "" = autodetectar
    "whisper_model": "small",
    "quality": 720,
}
SEG_SECONDS = 15
CHUNK_SECONDS = 300
FINAL = {"done", "error", "stopped"}


def clean_settings(raw: dict | None) -> dict:
    s = dict(DEFAULTS)
    raw = raw or {}
    for k, default in DEFAULTS.items():
        if k not in raw or raw[k] is None:
            continue
        v = raw[k]
        try:
            if isinstance(default, bool):
                s[k] = bool(v)
            elif isinstance(default, int):
                s[k] = int(v)
            elif isinstance(default, float):
                s[k] = float(v)
            elif isinstance(default, list):
                s[k] = [str(x).strip() for x in v if str(x).strip()][:50]
            else:
                s[k] = str(v)
        except (TypeError, ValueError):
            pass
    s["sounds"] = [g for g in s["sounds"] if g in SOUND_GROUPS]
    s["sensitivity"] = float(np.clip(s["sensitivity"], 0, 1))
    s["pre"] = float(np.clip(s["pre"], 0, 120))
    s["post"] = float(np.clip(s["post"], 1, 180))
    s["max_len"] = float(np.clip(s["max_len"], 5, 600))
    s["max_clips"] = int(np.clip(s["max_clips"], 1, 200))
    s["quality"] = int(np.clip(s["quality"], 240, 2160))
    if s["layout"] not in ("vertical_blur", "vertical_crop", "original"):
        s["layout"] = "vertical_blur"
    if s["whisper_model"] not in ("tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"):
        s["whisper_model"] = "small"
    return s


def _js_runtimes() -> dict:
    return {name: {} for name in ("deno", "node", "bun") if shutil.which(name)}


class Job:
    def __init__(self, url: str, mode: str, settings: dict, local_file: str | None = None, job_id: str | None = None):
        self.id = job_id or uuid.uuid4().hex[:10]
        self.url = url
        self.mode = mode  # auto | vod | live
        self.settings = settings
        self.local_file = local_file
        self.dir = JOBS_DIR / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.title = url
        self.status = "queued"
        self.message = "En cola"
        self.progress = 0.0
        self.duration = 0.0
        self.created = time.time()
        self.hits: list[dict] = []
        self.clips: list[dict] = []
        self.log: list[str] = []
        self.source: str | None = None
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self._procs: list[subprocess.Popen] = []
        self._speech_ok = True
        self._words: list[Word] = []  # transcripción completa (si se hizo)
        self._full_transcript = False

    # ------------------------------------------------------------- estado
    def say(self, msg: str, status: str | None = None, progress: float | None = None) -> None:
        with self.lock:
            self.message = msg
            if status:
                self.status = status
            if progress is not None:
                self.progress = float(np.clip(progress, 0, 1))
            self.log.append(f"{time.strftime('%H:%M:%S')}  {msg}")
            self.log = self.log[-200:]
        self.save()

    def public(self, full: bool = True) -> dict:
        with self.lock:
            d = {
                "id": self.id, "url": self.url, "mode": self.mode, "title": self.title,
                "status": self.status, "message": self.message, "progress": round(self.progress, 3),
                "duration": round(self.duration, 1), "created": self.created,
                "clips": list(self.clips), "settings": self.settings,
            }
            if full:
                d["hits"] = list(self.hits)
                d["log"] = list(self.log[-60:])
            return d

    def save(self) -> None:
        with self.lock:
            data = self.public()
            data["source"] = self.source
            data["local_file"] = self.local_file
            tmp = self.dir / "job.json.tmp"
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.dir / "job.json")

    @classmethod
    def load(cls, path: Path) -> "Job":
        d = json.loads(path.read_text(encoding="utf-8"))
        j = cls(d["url"], d.get("mode", "vod"), clean_settings(d.get("settings")), d.get("local_file"), d["id"])
        j.title, j.status, j.message = d.get("title", j.url), d.get("status", "done"), d.get("message", "")
        j.progress, j.duration, j.created = d.get("progress", 1), d.get("duration", 0), d.get("created", time.time())
        j.hits, j.clips, j.log, j.source = d.get("hits", []), d.get("clips", []), d.get("log", []), d.get("source")
        if j.status not in FINAL:
            j.status, j.message = "error", "Interrumpido al reiniciar el servidor"
        return j

    # ---------------------------------------------------------- ejecución
    def run(self) -> None:
        try:
            if self.local_file:
                self.source = self.local_file
                if self.mode == "live":
                    self._run_live()
                else:
                    self._run_vod()
            else:
                info = self._resolve()
                if self.mode == "live" or (self.mode == "auto" and info.get("is_live")):
                    self.mode = "live"
                    self._run_live()
                else:
                    self.mode = "vod"
                    self._download(info)
                    self._run_vod()
            if self.status not in FINAL:
                n = len(self.clips)
                self.say(f"Listo: {n} clip{'s' if n != 1 else ''}", "stopped" if self.stop_event.is_set() else "done", 1)
        except Exception as exc:
            traceback.print_exc()
            self.say(f"Error: {exc}", "error")
        finally:
            self._kill()

    def stop(self) -> None:
        self.stop_event.set()
        if self.mode != "live":
            self._kill()

    def _kill(self) -> None:
        for p in self._procs:
            if p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=5)
                except Exception:
                    p.kill()
        self._procs.clear()

    # ------------------------------------------------------------ fuentes
    def _ydl_opts(self) -> dict:
        return {
            "quiet": True, "no_warnings": True, "noplaylist": True,
            "ffmpeg_location": ff.ffmpeg_bin(),
            "js_runtimes": _js_runtimes() or {"deno": {}},
        }

    def _resolve(self) -> dict:
        import yt_dlp

        self.say("Consultando el enlace…", "downloading", 0.01)
        with yt_dlp.YoutubeDL(self._ydl_opts()) as ydl:
            info = ydl.extract_info(self.url, download=False)
        self.title = info.get("title") or self.url
        self.duration = float(info.get("duration") or 0)
        return info

    def _download(self, info: dict) -> None:
        import yt_dlp

        q = self.settings["quality"]

        def hook(d: dict) -> None:
            if self.stop_event.is_set():
                raise yt_dlp.utils.DownloadCancelled("cancelado")
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                frac = d.get("downloaded_bytes", 0) / total if total else 0
                with self.lock:
                    self.progress = 0.02 + 0.28 * frac
                    self.message = f"Descargando video… {frac * 100:.0f}%"

        opts = self._ydl_opts() | {
            "format": f"bv*[height<={q}]+ba/b[height<={q}]/b",
            "outtmpl": str(self.dir / "source.%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [hook],
        }
        self.say("Descargando video…", "downloading", 0.02)
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([self.url])
        files = [p for p in self.dir.glob("source.*") if p.suffix not in (".part", ".ytdl")]
        if not files:
            raise RuntimeError("La descarga no produjo ningún archivo")
        self.source = str(max(files, key=lambda p: p.stat().st_size))

    # ------------------------------------------------------------ análisis
    def _analyze(self, audio: np.ndarray, offset: float, context: np.ndarray | None = None) -> list[Hit]:
        """Aplica todos los disparadores a un trozo de audio. Tiempos globales."""
        s = self.settings
        hits: list[Hit] = []
        if s["hype"]:
            if context is not None and len(context):
                joined = np.concatenate([context, audio])
                ctx_s = len(context) / SAMPLE_RATE
                hits += [Hit(h.t - ctx_s, h.kind, h.score) for h in detect_hype(joined, s["sensitivity"]) if h.t >= ctx_s]
            else:
                hits += detect_hype(audio, s["sensitivity"])
        if s["sounds"]:
            found = detect_sounds(audio, s["sounds"], s["sensitivity"])
            if found is None:
                if not getattr(self, "_warned_yamnet", False):
                    self._warned_yamnet = True
                    self.say("⚠ Modelo de sonidos no disponible (" + str(yamnet_status()["reason"])[:120]
                             + "). Sigo con palabras clave y picos de volumen.")
            else:
                hits += found
        if s["keywords"] and self._speech_ok:
            words = self._transcribe(audio, 0.0)
            self._words += [Word(w.start + offset, w.end + offset, w.text) for w in words]
            hits += find_keywords(words, s["keywords"])
        return [Hit(h.t + offset, h.kind, h.score, h.text) for h in hits]

    def _transcribe(self, audio: np.ndarray, offset: float) -> list[Word]:
        if not self._speech_ok:
            return []
        try:
            return transcribe(audio, self.settings["whisper_model"], self.settings["language"] or None, offset)
        except Exception as exc:
            self._speech_ok = False
            self.say(f"⚠ Transcripción desactivada: {str(exc)[:160]}")
            return []

    def _words_for(self, src: Path, start: float, end: float, global_start: float) -> list[Word]:
        """Palabras del clip en tiempos de `src`. Reusa la transcripción completa si existe."""
        s = self.settings
        if self._full_transcript:
            shift = start - global_start
            return [Word(w.start + shift, w.end + shift, w.text) for w in self._words
                    if w.end > global_start and w.start < global_start + (end - start)]
        if not (s["smart_titles"] or s["captions"]) or not self._speech_ok:
            return []
        return self._transcribe(ff.read_audio(src, start, end - start), start)

    # ----------------------------------------------------------------- VOD
    def _run_vod(self) -> None:
        src = Path(self.source)
        info = ff.probe(src)
        if not info["has_audio"]:
            raise RuntimeError("El video no tiene pista de audio para analizar")
        self.duration = total = info["duration"]
        s = self.settings
        self._full_transcript = bool(s["keywords"])
        hits: list[Hit] = []
        t = 0.0
        while t < total and not self.stop_event.is_set():
            self.say(f"Escuchando el video… {t / 60:.0f}/{total / 60:.0f} min", "analyzing", 0.3 + 0.4 * t / max(total, 1))
            audio = ff.read_audio(src, t, CHUNK_SECONDS)
            if not len(audio):
                break
            hits += self._analyze(audio, t)
            with self.lock:
                self.hits = [h.asdict() for h in hits]
            t += CHUNK_SECONDS
        if self.stop_event.is_set():
            return
        moments = build_moments(hits, s["pre"], s["post"], s["max_len"], total)
        moments = sorted(sorted(moments, key=lambda m: -m.score)[: s["max_clips"]], key=lambda m: m.start)
        if not moments:
            self.say("No se encontró ningún momento con esos disparadores. Sube la sensibilidad o añade palabras.", "done", 1)
            return
        for i, m in enumerate(moments):
            if self.stop_event.is_set():
                break
            self.say(f"Creando short {i + 1} de {len(moments)}…", "rendering", 0.7 + 0.3 * i / len(moments))
            self._make_clip(src, m.start, m.end, m, global_start=m.start)

    def _make_clip(self, src: Path, start: float, end: float, moment: Moment, global_start: float,
                   title: str | None = None, emoji: str | None = None) -> dict:
        s = self.settings
        words = self._words_for(src, start, end, global_start)
        # los hits están en tiempo global; el título se calcula en tiempo de `src`
        local = Moment(start, end, [Hit(h.t - global_start + start, h.kind, h.score, h.text) for h in moment.hits])
        auto_emoji, auto_title = make_title(local, words)
        cid = uuid.uuid4().hex[:8]
        clip = {
            "id": cid, "file": f"clip_{cid}.mp4", "thumb": f"clip_{cid}.jpg",
            "emoji": emoji if emoji is not None else auto_emoji,
            "title": title if title is not None else auto_title,
            "start": round(global_start, 2), "end": round(global_start + end - start, 2),
            "kinds": moment.kinds or ["manual"], "score": round(moment.score, 2),
            "text": " ".join(w.text for w in words)[:600],
            "src": src.name, "src_start": round(start, 3), "src_end": round(end, 3),
            "words": [w.asdict() for w in words],
        }
        self._render(clip)
        with self.lock:
            self.clips.append(clip)
            self.clips.sort(key=lambda c: c["start"])
        self.save()
        return clip

    def _render(self, clip: dict) -> None:
        s = self.settings
        src = Path(self.source) if clip["src"] == Path(self.source or "").name else self.dir / clip["src"]
        words = [Word(w["s"], w["e"], w["w"]) for w in clip.get("words", [])]
        render_clip(
            src, clip["src_start"], clip["src_end"], self.dir / clip["file"], layout=s["layout"],
            emoji=clip["emoji"], title=clip["title"], show_title=s["show_title"], words=words, captions=s["captions"],
        )

    def retitle(self, clip_id: str, title: str, emoji: str) -> dict:
        clip = next((c for c in self.clips if c["id"] == clip_id), None)
        if clip is None:
            raise KeyError(clip_id)
        clip["title"], clip["emoji"] = title.strip()[:120], emoji.strip()[:8]
        self._render(clip)
        clip["v"] = clip.get("v", 0) + 1  # rompe la caché del navegador
        self.save()
        return clip

    def manual_clip(self, start: float, end: float, title: str, emoji: str) -> dict:
        if not self.source or self.mode == "live":
            raise RuntimeError("El recorte manual solo está disponible para videos descargados")
        start = max(0.0, start)
        end = min(end, self.duration or end)
        if end - start < 1:
            raise RuntimeError("El rango debe durar al menos 1 segundo")
        return self._make_clip(Path(self.source), start, end, Moment(start, end, []), start,
                               title=title or None, emoji=emoji or None)

    def delete_clip(self, clip_id: str) -> None:
        with self.lock:
            for c in list(self.clips):
                if c["id"] == clip_id:
                    self.clips.remove(c)
                    for name in (c["file"], c["thumb"]):
                        (self.dir / name).unlink(missing_ok=True)
                    if c["src"].startswith("raw_"):
                        (self.dir / c["src"]).unlink(missing_ok=True)
        self.save()

    # ------------------------------------------------------------- EN VIVO
    def _start_capture(self, seg_dir: Path, first_index: int) -> None:
        seg_args = [
            "-c", "copy", "-f", "segment", "-segment_time", str(SEG_SECONDS), "-reset_timestamps", "1",
            "-segment_start_number", str(first_index), "-segment_list", str(seg_dir / f"list_{first_index}.csv"),
            "-segment_list_type", "csv", "-segment_list_flags", "+live", str(seg_dir / "seg_%06d.ts"),
        ]
        base = [ff.ffmpeg_bin(), "-hide_banner", "-nostdin", "-loglevel", "error", "-y"]
        errlog = open(self.dir / "capture.log", "ab")  # para diagnosticar fallos de captura
        if self.local_file:  # simulación de directo con un archivo (pruebas)
            p = subprocess.Popen(base + ["-re", "-i", self.local_file] + seg_args, stderr=errlog)
            errlog.close()
            self._procs = [p]
            return
        q = self.settings["quality"]
        ytdlp = [sys.executable, "-m", "yt_dlp", "--no-progress", "--no-playlist",
                 "-f", f"b[height<={q}]/b", "--ffmpeg-location", ff.ffmpeg_bin()]
        for rt in _js_runtimes():
            ytdlp += ["--js-runtimes", rt]
        ytdlp += ["-o", "-", self.url]
        dl = subprocess.Popen(ytdlp, stdout=subprocess.PIPE, stderr=errlog)
        p = subprocess.Popen(base + ["-i", "pipe:0"] + seg_args, stdin=dl.stdout, stderr=errlog)
        dl.stdout.close()
        errlog.close()
        self._procs = [dl, p]

    def _capture_tail(self) -> str:
        """Últimas líneas útiles del registro de yt-dlp/ffmpeg."""
        try:
            text = (self.dir / "capture.log").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("[download]")]
        errs = [ln for ln in lines if "ERROR" in ln or "error" in ln.lower()] or lines
        return (" · Detalle: " + " | ".join(errs[-3:])[:600]) if errs else ""

    def _run_live(self) -> None:
        s = self.settings
        seg_dir = self.dir / "segments"
        seg_dir.mkdir(exist_ok=True)
        segs: list[tuple[Path, float, float]] = []  # (archivo, t0, t1) en tiempo global de la grabación
        seen: set[str] = set()
        clock = 0.0
        context = np.zeros(0, dtype=np.float32)
        open_m: Moment | None = None
        restarts = 0
        self._start_capture(seg_dir, 0)
        self.say("🔴 Grabando el directo y escuchando…", "live", 0)
        keep = s["pre"] + s["max_len"] + 3 * SEG_SECONDS

        def new_segments() -> list[tuple[Path, float]]:
            out = []
            for lst in sorted(seg_dir.glob("list_*.csv")):
                try:
                    rows = list(csv.reader(lst.read_text(encoding="utf-8").splitlines()))
                except OSError:
                    continue
                for row in rows:
                    if len(row) >= 3 and row[0] not in seen:
                        seen.add(row[0])
                        out.append((seg_dir / row[0], max(0.1, float(row[2]) - float(row[1]))))
            return out

        def finalize(m: Moment) -> None:
            use = [x for x in segs if x[2] > m.start and x[1] < m.end and x[0].exists()]
            if not use:
                return
            cid = uuid.uuid4().hex[:8]
            raw = self.dir / f"raw_{cid}.ts"
            lst = self.dir / f"raw_{cid}.txt"
            lst.write_text("".join(f"file '{p.as_posix()}'\n" for p, _, _ in use), encoding="utf-8")
            try:
                ff.run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)])
            finally:
                lst.unlink(missing_ok=True)
            g0 = use[0][1]
            a, b = max(0.0, m.start - g0), min(m.end, use[-1][2]) - g0
            self.say(f"✂ Momento detectado en {_clock(m.start)} — creando short…")
            try:
                self._make_clip(raw, a, b, m, global_start=g0 + a)
            except Exception as exc:
                self.say(f"⚠ No se pudo crear el clip: {str(exc)[:200]}")

        while True:
            stopping = self.stop_event.is_set()
            alive = any(p.poll() is None for p in self._procs[-1:])
            if stopping:
                self._kill()
            fresh = new_segments()
            for path, dur in fresh:
                t0, clock = clock, clock + dur
                segs.append((path, t0, clock))
                try:
                    audio = ff.read_audio(path)
                except RuntimeError:
                    continue
                for h in self._analyze(audio, t0, context):
                    with self.lock:
                        self.hits.append(h.asdict())
                        self.hits = self.hits[-500:]
                    if open_m and h.t <= open_m.end:
                        open_m.hits.append(h)
                        if h.t + s["post"] - open_m.start <= s["max_len"]:
                            open_m.end = max(open_m.end, h.t + s["post"])
                    else:
                        if open_m:
                            finalize(open_m)
                        open_m = Moment(max(0.0, h.t - s["pre"]), h.t + s["post"], [h])
                context = np.concatenate([context, audio])[-45 * SAMPLE_RATE:]
                self.duration = clock
            if open_m and (clock >= open_m.end or stopping or not alive):
                finalize(open_m)
                open_m = None
            # borra segmentos viejos que ya no hacen falta
            limit = min(clock - keep, open_m.start - 1 if open_m else clock)
            while segs and segs[0][2] < limit:
                segs.pop(0)[0].unlink(missing_ok=True)
            if fresh:
                with self.lock:
                    self.message = f"🔴 En vivo · {_clock(clock)} grabados · {len(self.clips)} clips"
                self.save()
            if stopping:
                break
            if not alive and not fresh:
                if self.local_file or restarts >= 5 or clock == 0 and restarts >= 1:
                    if clock == 0:
                        raise RuntimeError("No se pudo capturar el directo (¿terminó o el enlace no es válido?)"
                                           + self._capture_tail())
                    break
                restarts += 1
                self.say(f"Reconectando al directo (intento {restarts})…")
                time.sleep(5)
                self._start_capture(seg_dir, len(seen) + 1000 * restarts)
            time.sleep(1.0)
        shutil.rmtree(seg_dir, ignore_errors=True)


def _clock(t: float) -> str:
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


# ---------------------------------------------------------------- gestor
class Manager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self._queue: "queue.Queue[Job]" = queue.Queue()
        for p in sorted(JOBS_DIR.glob("*/job.json")):
            try:
                j = Job.load(p)
                self.jobs[j.id] = j
            except Exception:
                continue
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        while True:
            job = self._queue.get()
            if not job.stop_event.is_set():
                job.run()

    def create(self, url: str, mode: str, settings: dict, local_file: str | None = None, job: Job | None = None) -> Job:
        job = job or Job(url, mode, clean_settings(settings), local_file)
        self.jobs[job.id] = job
        job.save()
        if mode == "live":  # los directos corren en paralelo, cada uno en su hilo
            threading.Thread(target=job.run, daemon=True).start()
        else:
            self._queue.put(job)
        return job

    def get(self, job_id: str) -> Job:
        return self.jobs[job_id]

    def delete(self, job_id: str) -> None:
        job = self.jobs.pop(job_id)
        job.stop()
        job._kill()
        for _ in range(3):
            shutil.rmtree(job.dir, ignore_errors=True)
            if not job.dir.exists():
                break
            time.sleep(0.5)


if os.name == "nt":  # evita ventanas de consola al lanzar ffmpeg en Windows
    _orig_popen = subprocess.Popen.__init__

    def _quiet_popen(self, *a, **kw):
        kw.setdefault("creationflags", 0x08000000)
        _orig_popen(self, *a, **kw)

    subprocess.Popen.__init__ = _quiet_popen
