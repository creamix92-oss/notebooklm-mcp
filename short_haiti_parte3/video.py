"""Vídeo vertical (1080x1920, 30 fps) de «Las siete invasiones haitianas», sincronizado con la narración.

Uso: python3 video.py <carpeta_datos> <tiempos.json> <carpeta_salida> [segundos,de,vista,previa]
Datos: Natural Earth 10m (dominio público).
"""
import json
import math
import multiprocessing as mp
import shutil
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escenas import SCENES, ESP, HESP, AVANCE  # noqa: E402

DATA, TIEMPOS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FRAMES = OUT / "frames"
FPS, CRS = 30, "EPSG:3857"
TIMES = json.loads(TIEMPOS.read_text())
DURATION = TIMES[-1][1]
MOVE = 1.2  # segundos de movimiento de cámara

OCEAN, LAND, BORDER, INK = "#16324F", "#D9D2C3", "#7A7468", "#0B1A2A"

world = gpd.read_file(DATA / "ne_10m_admin_0_countries.geojson", columns=["ADM0_A3", "geometry"])
world = gpd.clip(world, box(-100, 5, -55, 32))
hti, dom = world[world.ADM0_A3 == "HTI"], world[world.ADM0_A3 == "DOM"]
frontera = hti.union_all().boundary.intersection(dom.union_all().buffer(0.01))

def P(g):
    return g.to_crs(CRS) if isinstance(g, (gpd.GeoDataFrame, gpd.GeoSeries)) else gpd.GeoSeries([g], crs=4326).to_crs(CRS)

def xy(lon, lat):
    return 6378137.0 * math.radians(lon), 6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def scene_at(t):
    for i, (a, b) in enumerate(TIMES):
        if a <= t < b:
            return i, t - a
    return len(TIMES) - 1, t - TIMES[-1][0]

def camera(i, dt):
    x1, y1, w1 = SCENES[i]["cam"]
    if i == 0:
        return x1, y1, w1
    x0, y0, w0 = SCENES[i - 1]["cam"]
    u = ease(dt / MOVE)
    w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
    k = u if abs(w0 - w1) < 1e-9 else (w0 - w) / (w0 - w1)
    return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, w

# --- Dibujo ----------------------------------------------------------------------
fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)
P(world[~world.ADM0_A3.isin(["HTI", "DOM"])]).plot(ax=ax, color=LAND, edgecolor=BORDER, linewidth=0.8)
P(hti).plot(ax=ax, color="#D7263D", linewidth=0); west = ax.collections[-1]
P(dom).plot(ax=ax, color="#3A8DDE", linewidth=0); east = ax.collections[-1]
P(world[world.ADM0_A3.isin(["HTI", "DOM"])].union_all().boundary).plot(ax=ax, color="white", linewidth=1.5)
P(frontera).plot(ax=ax, color="white", linewidth=5, zorder=8); border = ax.collections[-1]

stroke = lambda w: [pe.withStroke(linewidth=w, foreground=INK)]
t_title = fig.text(0.5, 0.925, "", fontsize=58, color="white", weight="bold", ha="center", va="center", path_effects=stroke(10))
t_sub = fig.text(0.5, 0.862, "", fontsize=34, color="#F2E6C9", ha="center", va="center", path_effects=stroke(7), linespacing=1.2)
fig.text(0.5, 0.05, "Mapa: Natural Earth (dominio público) · Rutas y lugares aproximados", fontsize=18,
         color="white", ha="center", path_effects=stroke(4))
fig.text(0.5, 0.027, "Línea discontinua: ruta no confirmada · Naranja: retirada", fontsize=18,
         color="white", ha="center", path_effects=stroke(4))

region_art = {}
for sc in SCENES:
    for lon, lat, name in sc.get("etiquetas", []):
        if (lon, lat, name) not in region_art:
            x, y = xy(lon, lat)
            region_art[(lon, lat, name)] = ax.text(x, y, name, fontsize=36, color="white", weight="bold", ha="center",
                                                   va="center", zorder=10, linespacing=1.1, path_effects=stroke(6))

OFFS = {"arriba": ((0, 24), "center", "bottom"), "abajo": ((0, -24), "center", "top"),
        "der": ((22, 0), "left", "center"), "izq": ((-22, 0), "right", "center")}
marker_art = {}
for sc in SCENES:
    for m in sc.get("marcas", []):
        if tuple(m) in marker_art:
            continue
        lon, lat, name, d = m
        x, y = xy(lon, lat)
        dot = ax.scatter([x], [y], s=240, color="white", edgecolor=INK, linewidth=3, zorder=11)
        off, ha, va = OFFS[d]
        txt = ax.annotate(name, (x, y), xytext=off, textcoords="offset points", fontsize=28, color="white",
                          weight="bold", ha=ha, va=va, zorder=12, path_effects=stroke(6))
        marker_art[tuple(m)] = (dot, txt)

# Rutas: una línea con trazo parcial, una punta de flecha y un rótulo por ruta de cada escena
route_art = {}
for i, sc in enumerate(SCENES):
    for j, r in enumerate(sc.get("rutas", [])):
        pts = [xy(*p) for p in r["pts"]]
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        color = r.get("color", AVANCE)
        ls = (0, (1.6, 1.1)) if r.get("dash") else "-"
        line = Line2D([], [], color=color, linewidth=11, linestyle=ls, solid_capstyle="round", zorder=9,
                      path_effects=[pe.withStroke(linewidth=17, foreground=INK)])
        ax.add_line(line)
        head = FancyArrowPatch((0, 0), (1, 1), arrowstyle="-|>,head_length=30,head_width=17", mutation_scale=1,
                               color=color, linewidth=2, zorder=9)
        ax.add_patch(head)
        label = None
        if r.get("texto"):
            label = ax.annotate(r["texto"], pts[0], xytext=(-18, 0), textcoords="offset points", fontsize=26,
                                color=color, weight="bold", ha="right", va="center", zorder=12, path_effects=stroke(6))
        route_art[(i, j)] = dict(pts=pts, cum=cum, line=line, head=head, label=label)

ficha_art = []
for sc in SCENES:
    ficha_art.append(fig.text(0.06, 0.335, "\n".join(sc["ficha"]), fontsize=30, color="white", ha="left", va="top",
                              linespacing=1.45, zorder=20, family="DejaVu Sans",
                              bbox=dict(boxstyle="round,pad=0.7", fc="#0B1A2A", ec="#3E5C7A", alpha=0.88)))

def route_fractions(i, dt):
    """Cada ruta se dibuja durante la escena; los tiempos se estiran para ocupar ~70 % de ella."""
    sc, a, b = SCENES[i], *TIMES[i]
    rutas = sc.get("rutas", [])
    if not rutas:
        return ()
    fin = max(r.get("delay", 1.2) + r.get("dur", 3.0) for r in rutas)
    k = max(1.0, 0.7 * (b - a) / fin)
    return tuple(round(ease((dt - r.get("delay", 1.2) * k) / (r.get("dur", 3.0) * k)), 2) for r in rutas)

def state(t):
    i, dt = scene_at(t)
    cx, cy, w = camera(i, dt)
    return i, (round(cx, 5), round(cy, 5), round(w, 5)), route_fractions(i, dt)

def fit(art, text, size):
    art.set_text(text); art.set_fontsize(size)
    wpx = art.get_window_extent(fig.canvas.get_renderer()).width
    if wpx > 0.9 * 1080:
        art.set_fontsize(size * 0.9 * 1080 / wpx)

def draw(st):
    i, (cx, cy, w), fracs = st
    sc = SCENES[i]
    x0, y = xy(cx - w / 2, cy); x1, _ = xy(cx + w / 2, cy)
    h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(y - h / 2, y + h / 2)
    fit(t_title, sc["titulo"], 58); fit(t_sub, sc["sub"], 34)
    west.set_facecolor(sc["oeste"]); east.set_facecolor(sc["este"])
    border.set_visible(sc["oeste"] != sc["este"])
    for k, art in enumerate(ficha_art):
        art.set_visible(k == i)
    labels = set(sc.get("etiquetas", []))
    for key, art in region_art.items():
        art.set_visible(key in labels)
    shown = {tuple(m) for m in sc.get("marcas", [])}
    for key, (dot, txt) in marker_art.items():
        dot.set_visible(key in shown); txt.set_visible(key in shown)
    head_len = 0.028 * (x1 - x0)
    for (si, j), art in route_art.items():
        active = si == i and j < len(fracs) and fracs[j] > 0
        art["line"].set_visible(active); art["head"].set_visible(active)
        if art["label"]:
            art["label"].set_visible(si == i)
        if not active:
            continue
        pts, cum = art["pts"], art["cum"]
        d = fracs[j] * cum[-1]
        xs, ys = [pts[0][0]], [pts[0][1]]
        for k in range(1, len(pts)):
            if cum[k] <= d:
                xs.append(pts[k][0]); ys.append(pts[k][1])
            else:
                u = (d - cum[k - 1]) / (cum[k] - cum[k - 1])
                xs.append(pts[k - 1][0] + (pts[k][0] - pts[k - 1][0]) * u)
                ys.append(pts[k - 1][1] + (pts[k][1] - pts[k - 1][1]) * u)
                break
        art["line"].set_data(xs, ys)
        tip = (xs[-1], ys[-1])
        bx, by = xs[-2] if len(xs) > 1 else xs[-1], ys[-2] if len(ys) > 1 else ys[-1]
        L = math.hypot(tip[0] - bx, tip[1] - by) or 1.0
        back = (tip[0] - (tip[0] - bx) / L * head_len, tip[1] - (tip[1] - by) / L * head_len)
        art["head"].set_positions(back, tip)

def render(job):
    st, f = job
    draw(st); fig.savefig(f, dpi=100, facecolor=OCEAN)
    return f

if __name__ == "__main__" and len(sys.argv) > 4:  # vista previa: segundos sueltos
    OUT.mkdir(parents=True, exist_ok=True)
    for sec in sys.argv[4].split(","):
        draw(state(float(sec))); fig.savefig(OUT / f"preview_{sec}.png", dpi=100, facecolor=OCEAN)
    sys.exit()

if __name__ == "__main__":
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)
    n = int(FPS * DURATION)
    states = [state(i / FPS) for i in range(n)]
    owner, jobs = [], []
    for i, st in enumerate(states):
        if i and st == states[i - 1]:
            owner.append(owner[-1])
        else:
            owner.append(i); jobs.append((st, FRAMES / f"{i:05d}.png"))
    print(f"{len(jobs)} fotogramas únicos de {n}", flush=True)
    with mp.get_context("fork").Pool(4) as pool:
        for k, _ in enumerate(pool.imap_unordered(render, jobs, chunksize=8)):
            if k % 300 == 0:
                print(f"{k}/{len(jobs)}", flush=True)
    for i, o in enumerate(owner):
        if o != i:
            shutil.copyfile(FRAMES / f"{o:05d}.png", FRAMES / f"{i:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "video_sin_voz.mp4")], check=True)
    shutil.rmtree(FRAMES)
    print("ok")
