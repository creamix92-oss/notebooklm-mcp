"""Renderizado del short: recorte, formato vertical, título con emoji y subtítulos."""
from __future__ import annotations

import os
import sys
import textwrap
from functools import lru_cache
from pathlib import Path

from . import ff
from .speech import Word

W, H = 1080, 1920


# ------------------------------------------------------------------ fuentes
def _first_existing(paths: list[str]) -> str | None:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


@lru_cache(maxsize=1)
def _text_font_path() -> str | None:
    win = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    return _first_existing(
        [
            os.path.join(win, "seguisb.ttf"),
            os.path.join(win, "arialbd.ttf"),
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]
    )


@lru_cache(maxsize=1)
def _emoji_font_path() -> str | None:
    win = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    return _first_existing(
        [
            os.path.join(win, "seguiemj.ttf"),
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf",
        ]
    )


def _emoji_image(emoji: str, size: int):
    """Dibuja el emoji a color; None si el sistema no tiene fuente de emojis."""
    from PIL import Image, ImageDraw, ImageFont

    path = _emoji_font_path()
    if not path or not emoji:
        return None
    for px in (109, 160, 137, 96, 64):  # tamaños válidos según la fuente (bitmap o vectorial)
        try:
            font = ImageFont.truetype(path, px)
            box = font.getbbox(emoji)
            w, h = max(1, box[2] - box[0]), max(1, box[3] - box[1])
            img = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
            ImageDraw.Draw(img).text((4 - box[0], 4 - box[1]), emoji, font=font, embedded_color=True)
            if img.getbbox() is None:
                continue
            img = img.crop(img.getbbox())
            scale = size / img.height
            return img.resize((max(1, int(img.width * scale)), size), Image.LANCZOS)
        except Exception:
            continue
    return None


def make_title_overlay(path: Path, emoji: str, title: str, width: int, height: int, top: int, bottom: int | None = None) -> bool:
    """PNG transparente del tamaño del video con «emoji + título» centrado en `top`."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    fs = max(22, int(width * 0.066))
    fpath = _text_font_path()
    try:
        font = ImageFont.truetype(fpath, fs) if fpath else ImageFont.load_default(fs)
    except Exception:
        font = ImageFont.load_default()
    max_chars = max(10, int(width * 0.86 / (fs * 0.56)))
    lines = textwrap.wrap(title, max_chars) if title else []
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][: max_chars - 1].rstrip() + "…"
    em = _emoji_image(emoji, int(fs * 1.7))
    line_h = int(fs * 1.22)
    if bottom is not None:  # ancla el bloque por abajo para que no tape el video
        block = (em.height + int(fs * 0.35) if em is not None else 0) + (line_h * len(lines) + 2 * int(fs * 0.4) if lines else 0)
        top = max(int(height * 0.03), bottom - block)
    y = top
    if em is not None:
        canvas.alpha_composite(em, ((width - em.width) // 2, y))
        y += em.height + int(fs * 0.35)
    if lines:
        widths = [draw.textlength(ln, font=font) for ln in lines]
        pad_x, pad_y = int(fs * 0.6), int(fs * 0.4)
        bw = int(max(widths)) + 2 * pad_x
        bh = line_h * len(lines) + 2 * pad_y
        bx = (width - bw) // 2
        draw.rounded_rectangle((bx, y, bx + bw, y + bh), radius=int(fs * 0.5), fill=(255, 255, 255, 240))
        ty = y + pad_y
        for ln, lw in zip(lines, widths):
            draw.text(((width - lw) // 2, ty), ln, font=font, fill=(12, 12, 16, 255))
            ty += line_h
    if em is None and not lines:
        return False
    canvas.save(path)
    return True


# ---------------------------------------------------------------- subtítulos
def _ass_time(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_captions(path: Path, words: list[Word], clip_start: float, clip_len: float, width: int, height: int, margin_v: int) -> bool:
    """Subtítulos estilo short: grupos de 2–4 palabras en mayúsculas."""
    ws = [w for w in words if w.end > clip_start and w.start < clip_start + clip_len]
    if not ws:
        return False
    groups: list[list[Word]] = []
    cur: list[Word] = []
    for w in ws:
        if cur and (len(cur) >= 4 or w.start - cur[-1].end > 0.6 or sum(len(x.text) for x in cur) + len(w.text) > 22):
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    fs = int(width * 0.075)
    head = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {width}\nPlayResY: {height}\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        f"Style: C,Arial,{fs},&H00FFFFFF,&H00000000,&H80000000,-1,1,{max(2, fs // 12)},1,2,40,40,{margin_v}\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
    )
    lines = []
    for i, g in enumerate(groups):
        s = g[0].start - clip_start
        e = g[-1].end - clip_start
        if i + 1 < len(groups):
            e = min(max(e, s + 0.35), groups[i + 1][0].start - clip_start)
        e = min(max(e, s + 0.2), clip_len)
        text = " ".join(w.text for w in g).upper().replace("{", "(").replace("}", ")").replace("\n", " ")
        lines.append(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},C,{text}")
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return True


# -------------------------------------------------------------------- render
def render_clip(
    src: Path,
    start: float,
    end: float,
    out: Path,
    layout: str = "vertical_blur",
    emoji: str = "",
    title: str = "",
    show_title: bool = True,
    words: list[Word] | None = None,
    captions: bool = False,
) -> None:
    """Corta [start, end] de `src` y genera el MP4 final + miniatura JPG."""
    dur = max(0.5, end - start)
    info = ff.probe(src)
    sw, sh = info.get("width") or 1280, info.get("height") or 720
    work = out.parent
    stem = out.stem
    title_bottom: int | None = None

    if layout == "original":
        ow, oh = (sw // 2) * 2, (sh // 2) * 2
        base = f"[0:v]scale={ow}:{oh},setsar=1,fps=30[base]"
        title_top = int(oh * 0.05)
        cap_margin = int(oh * 0.08)
    else:
        ow, oh = W, H
        if layout == "vertical_crop" or sh >= sw:
            base = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30[base]"
            title_top, cap_margin = int(H * 0.09), int(H * 0.16)
        else:  # video horizontal centrado sobre su propio fondo desenfocado
            fg_h = int(W * sh / sw / 2) * 2
            base = (
                f"[0:v]fps=30,split[a][b];"
                f"[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=8:2,"
                f"scale={W}:{H},eq=brightness=-0.12:saturation=1.15[bg];"
                f"[b]scale={W}:{fg_h}[fg];[bg][fg]overlay=0:(H-h)/2,setsar=1[base]"
            )
            top_free = (H - fg_h) // 2
            title_top = max(int(H * 0.06), top_free - int(H * 0.2))
            title_bottom = top_free - int(H * 0.02) if top_free > H * 0.15 else None
            cap_margin = max(int(H * 0.08), top_free - int(H * 0.11))

    inputs = ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src)]
    chain = base
    last = "base"
    png = work / f"{stem}.title.png"
    ass = work / f"{stem}.ass"
    if show_title and (title or emoji) and make_title_overlay(png, emoji, title, ow, oh, title_top, title_bottom):
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(png)]
        chain += f";[{last}][1:v]overlay=0:0:shortest=1[t]"
        last = "t"
    if captions and words and write_captions(ass, words, start, dur, ow, oh, cap_margin):
        chain += f";[{last}]subtitles={ass.name}[c]"  # ruta relativa: se ejecuta con cwd=work
        last = "c"

    args = [*inputs, "-filter_complex", chain, "-map", f"[{last}]"]
    if info.get("has_audio"):
        args += ["-map", "0:a:0", "-c:a", "aac", "-b:a", "160k", "-ar", "44100"]
    args += [
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-t", f"{dur:.3f}", str(out),
    ]
    try:
        ff.run(args, cwd=work)
    finally:
        for tmp in (png, ass):
            tmp.unlink(missing_ok=True)
    try:
        ff.run(["-ss", f"{min(dur / 2, 3):.2f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "4",
                str(out.with_suffix(".jpg"))])
    except RuntimeError as exc:  # la miniatura es opcional
        print("miniatura:", exc, file=sys.stderr)
