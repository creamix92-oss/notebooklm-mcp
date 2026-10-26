"""Vídeo vertical (1080x1920, 30 fps, 60 s) del short «Haití y República Dominicana».

Uso: python3 haiti.py <carpeta_datos> <carpeta_salida> [segundos,de,vista,previa]
Datos: Natural Earth 10m (dominio público).
"""
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
from shapely.geometry import box

DATA, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FRAMES = OUT / "frames"
FPS, DURATION = 30, 60.0
CRS = "EPSG:3857"

OCEAN, LAND, BORDER, INK = "#16324F", "#D9D2C3", "#7A7468", "#0B1A2A"
ESP, FRA, HTI, DOM, NEUTRO = "#FFC400", "#8E7CC3", "#D7263D", "#3A8DDE", "#BDB5A6"

# --- Datos -------------------------------------------------------------------
world = gpd.read_file(DATA / "ne_10m_admin_0_countries.geojson", columns=["ADM0_A3", "geometry"])
world = gpd.clip(world, box(-100, 5, -55, 32))
hti, dom = world[world.ADM0_A3 == "HTI"], world[world.ADM0_A3 == "DOM"]
frontera = hti.union_all().boundary.intersection(dom.union_all().buffer(0.01))

def P(g):
    return g.to_crs(CRS) if isinstance(g, (gpd.GeoDataFrame, gpd.GeoSeries)) else gpd.GeoSeries([g], crs=4326).to_crs(CRS)

def xy(lon, lat):
    return 6378137.0 * math.radians(lon), 6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

# --- Cámara ------------------------------------------------------------------
# (segundo, lon, lat, ancho en grados de longitud)
KEYS = [
    (0.0, -76.0, 19.5, 34.0),   # Caribe
    (5.0, -71.4, 18.9, 6.9),    # La Española: la cámara se queda en la isla
    (50.0, -71.4, 18.9, 6.6),
    (54.0, -71.7, 19.0, 3.2),   # zoom a la frontera
    (60.0, -71.7, 19.0, 3.0),
]

def ease(u):
    return u * u * (3 - 2 * u)

def camera(t):
    for (t0, x0, y0, w0), (t1, x1, y1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / (t1 - t0))
            w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
            k = u if abs(w0 - w1) < 1e-9 else (w0 - w) / (w0 - w1)
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, w
    return KEYS[-1][1:]

# --- Escenas ----------------------------------------------------------------------
# (inicio, fin, título, subtítulo, color oeste, color este)
SCENES = [
    (0.0, 5.0, "Se independizó…", "…¡pero no de España!", HTI, DOM),
    (5.0, 12.0, "La Española", "Una isla, dos países", HTI, DOM),
    (12.0, 20.0, "1492", "Llega Colón: toda la isla es española", ESP, ESP),
    (20.0, 29.0, "1697 · Tratado de Ryswick", "Francia se queda con el oeste", FRA, ESP),
    (29.0, 38.0, "1804", "Nace Haití tras una rebelión\nde esclavos", HTI, NEUTRO),
    (38.0, 46.0, "1822 – 1844", "Haití ocupa toda la isla", HTI, HTI),
    (46.0, 54.0, "27 de febrero de 1844", "Independencia dominicana…\n¡de Haití!", HTI, DOM),
    (54.0, 60.0, "Una isla, dos países", "Y una frontera de casi 400 km", HTI, DOM),
]
# (inicio, fin, lon, lat, texto, tamaño, color)
LABELS = [
    (5.0, 12.0, -72.75, 19.05, "HAITÍ", 40, "white"),
    (5.0, 12.0, -70.35, 18.85, "REPÚBLICA\nDOMINICANA", 34, "white"),
    (12.0, 20.0, -71.0, 18.9, "ESPAÑA", 46, INK),
    (20.0, 29.0, -72.75, 19.05, "FRANCIA", 36, "white"),
    (20.0, 29.0, -70.35, 18.85, "ESPAÑA", 40, INK),
    (29.0, 38.0, -72.75, 19.05, "HAITÍ", 40, "white"),
    (38.0, 46.0, -71.0, 18.9, "HAITÍ", 46, "white"),
    (46.0, 50.0, -72.75, 19.05, "HAITÍ", 40, "white"),
    (46.0, 50.0, -70.35, 18.85, "REPÚBLICA\nDOMINICANA", 34, "white"),
    (54.0, 60.0, -72.45, 19.25, "HAITÍ", 44, "white"),
    (54.0, 60.0, -70.95, 18.8, "REPÚBLICA\nDOMINICANA", 38, "white"),
    (0.0, 5.0, -79.5, 21.7, "CUBA", 30, INK),
]

# --- Dibujo ----------------------------------------------------------------------
fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)
P(world[~world.ADM0_A3.isin(["HTI", "DOM"])]).plot(ax=ax, color=LAND, edgecolor=BORDER, linewidth=0.8)
P(hti).plot(ax=ax, color=HTI, linewidth=0); west = ax.collections[-1]
P(dom).plot(ax=ax, color=DOM, linewidth=0); east = ax.collections[-1]
P(world[world.ADM0_A3.isin(["HTI", "DOM"])].union_all().boundary).plot(ax=ax, color="white", linewidth=1.5)
P(frontera).plot(ax=ax, color="white", linewidth=6, zorder=8); border = ax.collections[-1]

stroke = lambda w: [pe.withStroke(linewidth=w, foreground=INK)]
t_title = fig.text(0.5, 0.925, "", fontsize=60, color="white", weight="bold", ha="center", va="center", path_effects=stroke(10))
t_sub = fig.text(0.5, 0.865, "", fontsize=36, color="#F2E6C9", ha="center", va="center", path_effects=stroke(7), linespacing=1.2)
fig.text(0.5, 0.03, "Mapa: Natural Earth (dominio público) · Fronteras históricas aproximadas", fontsize=18,
         color="white", ha="center", path_effects=stroke(4))
label_artists = []
for (a, b, lon, lat, text, size, color) in LABELS:
    x, y = xy(lon, lat)
    art = ax.text(x, y, text, fontsize=size, color=color, weight="bold", ha="center", va="center", zorder=10,
                  linespacing=1.1, path_effects=stroke(6) if color != INK else [])
    label_artists.append((a, b, art))

def border_alpha(t):
    """La frontera solo se ve cuando hay dos países (y se resalta al final)."""
    sc = next(s for s in SCENES if s[0] <= t < s[1]) if t < 60 else SCENES[-1]
    if sc[4] == sc[5]:
        return 0.0
    return 1.0 if t >= 54 else 0.6

def state(t):
    cx, cy, w = camera(t)
    sc = next((s for s in SCENES if s[0] <= t < s[1]), SCENES[-1])
    labels = tuple(a <= t < b for a, b, _ in label_artists)
    return (round(cx, 5), round(cy, 5), round(w, 5)), sc[2:], labels, border_alpha(t)

def fit(art, text, size):
    art.set_text(text); art.set_fontsize(size)
    wpx = art.get_window_extent(fig.canvas.get_renderer()).width
    if wpx > 0.9 * 1080:
        art.set_fontsize(size * 0.9 * 1080 / wpx)

def draw(st):
    (cx, cy, w), (title, sub, cw, ce), labels, alpha = st
    x0, y = xy(cx - w / 2, cy); x1, _ = xy(cx + w / 2, cy)
    h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(y - h / 2, y + h / 2)
    fit(t_title, title, 60); fit(t_sub, sub, 36)
    west.set_facecolor(cw); east.set_facecolor(ce)
    for vis, (_, _, art) in zip(labels, label_artists):
        art.set_visible(vis)
    border.set_alpha(alpha); border.set_visible(alpha > 0)

def render(job):
    st, f = job
    draw(st); fig.savefig(f, dpi=100, facecolor=OCEAN)
    return f

if __name__ == "__main__" and len(sys.argv) > 3:  # vista previa: segundos sueltos
    OUT.mkdir(parents=True, exist_ok=True)
    for sec in sys.argv[3].split(","):
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
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "haiti_short.mp4")], check=True)
    for sec, name in [(2, "01_caribe"), (8, "02_hoy"), (16, "03_1492"), (25, "04_1697"), (34, "05_1804"),
                      (42, "06_ocupacion"), (50, "07_1844"), (58, "08_frontera")]:
        shutil.copyfile(FRAMES / f"{sec * FPS:05d}.png", OUT / f"{name}.png")
    shutil.rmtree(FRAMES)
    print("ok")
