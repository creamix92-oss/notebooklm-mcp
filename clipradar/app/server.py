"""API web de ClipRadar (FastAPI)."""
from __future__ import annotations

import io
import json
import re
import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from . import ff
from .audio_events import HYPE, SOUND_GROUPS, yamnet_status
from .config import JOBS_DIR, WEB_DIR
from .jobs import DEFAULTS, Job, Manager, clean_settings
from .speech import whisper_status

app = FastAPI(title="ClipRadar", docs_url=None, redoc_url=None)
manager = Manager()


class NewJob(BaseModel):
    url: str
    mode: str = "auto"
    settings: dict = {}


class TitleEdit(BaseModel):
    title: str = ""
    emoji: str = ""


class ManualClip(BaseModel):
    start: float
    end: float
    title: str = ""
    emoji: str = ""


def _job(job_id: str) -> Job:
    try:
        return manager.get(job_id)
    except KeyError:
        raise HTTPException(404, "Trabajo no encontrado")


@app.get("/api/status")
def status() -> dict:
    try:
        ffmpeg = ff.ffmpeg_bin()
    except RuntimeError as exc:
        ffmpeg = None
        err = str(exc)
    return {
        "ffmpeg": bool(ffmpeg), "ffmpeg_error": None if ffmpeg else err,
        "yamnet": yamnet_status(), "whisper": whisper_status(),
        "sounds": [{"id": k, "emoji": v["emoji"], "label": v["label"]} for k, v in SOUND_GROUPS.items()],
        "hype": HYPE, "defaults": DEFAULTS,
    }


@app.get("/api/jobs")
def list_jobs() -> list[dict]:
    return [j.public(full=False) for j in sorted(manager.jobs.values(), key=lambda j: -j.created)]


@app.post("/api/jobs")
def create_job(body: NewJob) -> dict:
    url = body.url.strip()
    if not re.match(r"^https?://", url):
        raise HTTPException(400, "Pega un enlace válido (https://…)")
    mode = body.mode if body.mode in ("auto", "vod", "live") else "auto"
    return manager.create(url, mode, body.settings).public()


@app.post("/api/upload")
def upload(file: UploadFile = File(...), settings: str = Form("{}"), mode: str = Form("vod")) -> dict:
    try:
        cfg = json.loads(settings)
    except json.JSONDecodeError:
        cfg = {}
    name = re.sub(r"[^\w.\- ]", "_", Path(file.filename or "video.mp4").name)[-80:] or "video.mp4"
    mode = "live" if mode == "live" else "vod"  # "live" = simular un directo con el archivo (pruebas)
    job = Job(name, mode, clean_settings(cfg))
    dest = job.dir / ("source" + (Path(name).suffix or ".mp4"))
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out, 1024 * 1024)
    job.local_file = str(dest)
    job.title = name
    return manager.create(name, mode, cfg, job=job).public()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return _job(job_id).public()


@app.post("/api/jobs/{job_id}/stop")
def stop_job(job_id: str) -> dict:
    job = _job(job_id)
    job.stop()
    if job.status == "queued":
        job.say("Cancelado", "stopped")
    return job.public()


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str) -> dict:
    _job(job_id)
    manager.delete(job_id)
    return {"ok": True}


@app.patch("/api/jobs/{job_id}/clips/{clip_id}")
def edit_clip(job_id: str, clip_id: str, body: TitleEdit) -> dict:
    try:
        return _job(job_id).retitle(clip_id, body.title, body.emoji)
    except KeyError:
        raise HTTPException(404, "Clip no encontrado")
    except RuntimeError as exc:
        raise HTTPException(500, str(exc))


@app.delete("/api/jobs/{job_id}/clips/{clip_id}")
def delete_clip(job_id: str, clip_id: str) -> dict:
    _job(job_id).delete_clip(clip_id)
    return {"ok": True}


@app.post("/api/jobs/{job_id}/clips")
def manual_clip(job_id: str, body: ManualClip) -> dict:
    try:
        return _job(job_id).manual_clip(body.start, body.end, body.title, body.emoji)
    except RuntimeError as exc:
        raise HTTPException(400, str(exc))


def _safe_name(clip: dict) -> str:
    base = re.sub(r'[\\/:*?"<>|\n\r\t]+', " ", f"{clip.get('emoji', '')} {clip.get('title', '')}").strip()
    return (base[:80] or clip["id"]) + ".mp4"


@app.get("/api/jobs/{job_id}/zip")
def download_zip(job_id: str):
    job = _job(job_id)
    buf = io.BytesIO()
    used: set[str] = set()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for i, c in enumerate(job.clips, 1):
            path = job.dir / c["file"]
            if path.exists():
                name = f"{i:02d} {_safe_name(c)}"
                while name in used:
                    name = f"{uuid.uuid4().hex[:4]} {name}"
                used.add(name)
                z.write(path, name)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="clips_{job_id}.zip"'})


@app.get("/media/{job_id}/{name}")
def media(job_id: str, name: str, download: int = 0):
    job = _job(job_id)
    if not re.fullmatch(r"clip_[0-9a-f]{8}\.(mp4|jpg)", name):
        raise HTTPException(404)
    path = (JOBS_DIR / job.id / name).resolve()
    if not path.is_file() or JOBS_DIR.resolve() not in path.parents:
        raise HTTPException(404)
    if download:
        clip = next((c for c in job.clips if c["file"] == name), {"id": name, "title": name})
        return FileResponse(path, media_type="video/mp4", filename=_safe_name(clip))
    return FileResponse(path)


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html", headers={"Cache-Control": "no-cache"})
