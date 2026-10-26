"""Vídeo vertical (1080x1920, 30 fps) de la parte 2, sincronizado con la narración.

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
from matplotlib.patches import FancyArrowPatch
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escenas import SCENES, ESP, FRA, HTI, DOM, HESP, NEUTRO  # noqa: E402

DATA, TIEMPOS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FRAMES = OUT / "frames"
FPS, CRS = 30, "EPSG:3857"
TIMES = json.loads(TIEMPOS.read_text())
DURATION = TIMES[-1][1]
MOVE, ARROW = 1.2, 1.5  # segundos de movimiento de cámara y de crecimiento de la flecha

OCEAN, LAND, BORDER, INK = "#16324F", "#D9D2C3", "#7A7468", "#0B1A2A"
NOMBRES = {HTI: "HAITÍ", DOM: "REPÚBLICA\nDOMINICANA", FRA: "FRANCIA", ESP: "ESPAÑA", HESP: "HAITÍ\nESPAÑOL", NEUTRO: ""}

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
P(hti).plot(ax=ax, color=HTI, linewidth=0); west = ax.collections[-1]
P(dom).plot(ax=ax, color=DOM, linewidth=0); east = ax.collections[-1]
P(world[world.ADM0_A3.isin(["HTI", "DOM"])].union_all().boundary).plot(ax=ax, color="white", linewidth=1.5)
P(frontera).plot(ax=ax, color="white", linewidth=5, zorder=8); border = ax.collections[-1]

stroke = lambda w: [pe.withStroke(linewidth=w, foreground=INK)]
t_title = fig.text(0.5, 0.925, "", fontsize=60, color="white", weight="bold", ha="center", va="center", path_effects=stroke(10))
t_sub = fig.text(0.5, 0.86, "", fontsize=36, color="#F2E6C9", ha="center", va="center", path_effects=stroke(7), linespacing=1.2)
fig.text(0.5, 0.03, "Mapa: Natural Earth (dominio público) · Fronteras y lugares aproximados", fontsize=18,
         color="white", ha="center", path_effects=stroke(4))

def region_text(lon, lat):
    x, y = xy(lon, lat)
    return ax.text(x, y, "", fontsize=38, color="white", weight="bold", ha="center", va="center", zorder=10,
                   linespacing=1.1, path_effects=stroke(6))

lbl_w, lbl_e, lbl_all = region_text(-72.75, 19.05), region_text(-70.4, 19.2), region_text(-70.6, 19.0)

# Marcadores: se crean todos y se muestran los de la escena
marker_art = {}
for sc in SCENES:
    for m in sc.get("marcas", []):
        lon, lat, name = m[:3]
        abajo = len(m) > 3  # etiqueta debajo del punto para no pisar a otra
        if tuple(m) in marker_art:
            continue
        x, y = xy(lon, lat)
        dot = ax.scatter([x], [y], s=260, color="white", edgecolor=INK, linewidth=3, zorder=11)
        txt = ax.annotate(name, (x, y), xytext=(0, -26 if abajo else 26), textcoords="offset points", fontsize=30,
                          color="white", weight="bold", ha="center", va="top" if abajo else "bottom", zorder=12, path_effects=stroke(6))
        marker_art[tuple(m)] = (dot, txt)

arrow = FancyArrowPatch((0, 0), (1, 1), arrowstyle="-|>,head_length=28,head_width=16", mutation_scale=1,
                        color="white", linewidth=9, zorder=9, connectionstyle="arc3,rad=-0.25")
ax.add_patch(arrow)

def state(t):
    i, dt = scene_at(t)
    sc = SCENES[i]
    cx, cy, w = camera(i, dt)
    grow = round(ease(dt / ARROW), 3) if sc.get("flecha") else 0.0
    return i, (round(cx, 5), round(cy, 5), round(w, 5)), grow

def fit(art, text, size):
    art.set_text(text); art.set_fontsize(size)
    wpx = art.get_window_extent(fig.canvas.get_renderer()).width
    if wpx > 0.9 * 1080:
        art.set_fontsize(size * 0.9 * 1080 / wpx)

def draw(st):
    i, (cx, cy, w), grow = st
    sc = SCENES[i]
    x0, y = xy(cx - w / 2, cy); x1, _ = xy(cx + w / 2, cy)
    h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(y - h / 2, y + h / 2)
    fit(t_title, sc["titulo"], 60); fit(t_sub, sc["sub"], 36)
    west.set_facecolor(sc["oeste"]); east.set_facecolor(sc["este"])
    same = sc["oeste"] == sc["este"]
    border.set_visible(not same)
    big = sc["cam"][2] >= 5
    lbl_all.set_text(NOMBRES[sc["oeste"]] if same else ""); lbl_all.set_visible(big and same)
    lbl_w.set_text(NOMBRES[sc["oeste"]]); lbl_w.set_visible(big and not same)
    lbl_e.set_text(NOMBRES[sc["este"]]); lbl_e.set_visible(big and not same)
    lbl_e.set_color(INK if sc["este"] in (ESP, HESP) else "white")
    lbl_e.set_path_effects([] if sc["este"] in (ESP, HESP) else stroke(6))
    shown = {tuple(m) for m in sc.get("marcas", [])}
    for key, (dot, txt) in marker_art.items():
        dot.set_visible(key in shown); txt.set_visible(key in shown)
    if grow > 0:
        (ax0, ay0), (ax1, ay1) = sc["flecha"]
        a, b = xy(ax0, ay0), xy(ax1, ay1)
        end = (a[0] + (b[0] - a[0]) * grow, a[1] + (b[1] - a[1]) * grow)
        arrow.set_positions(a, end); arrow.set_visible(True)
    else:
        arrow.set_visible(False)

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
            if k % 200 == 0:
                print(f"{k}/{len(jobs)}", flush=True)
    for i, o in enumerate(owner):
        if o != i:
            shutil.copyfile(FRAMES / f"{o:05d}.png", FRAMES / f"{i:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "video_sin_voz.mp4")], check=True)
    shutil.rmtree(FRAMES)
    print("ok")
