"""Vídeo vertical (1080x1920, 30 fps, 60 s) del short «¿Por qué Gibraltar es británico?».

Uso: python3 gibraltar.py <carpeta_datos> <carpeta_salida>
Datos: Natural Earth 10m (dominio público) y geoBoundaries gbOpen ESP/GIB/MAR (CC BY 4.0 / ODbL).
"""
import math
import shutil
import multiprocessing as mp
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
ESP, GIB, UK = "#FFC400", "#D7263D", "#D7263D"

# --- Datos -------------------------------------------------------------------
STRAIT = box(-6.8, 35.4, -4.2, 37.0)  # zona donde se usan fronteras detalladas
world = gpd.read_file(DATA / "ne_10m_admin_0_countries.geojson", columns=["ADM0_A3", "geometry"])
lakes = gpd.read_file(DATA / "ne_10m_lakes.geojson", columns=["geometry"])
world = gpd.clip(world, box(-30, 20, 40, 66))
world["geometry"] = world.geometry.difference(STRAIT)

def detailed(name):
    g = gpd.read_file(DATA / f"{name}_gb.geojson")
    g = gpd.clip(g, STRAIT)
    g["geometry"] = g.geometry.simplify(0.00005)
    return g

esp_d, gib_d, mar_d = detailed("esp"), detailed("gib"), detailed("mar")
# La verja: tramo del contorno de Gibraltar que toca España
verja = gib_d.boundary.union_all().intersection(esp_d.union_all().buffer(0.0008))

def P(g):
    return g.to_crs(CRS) if isinstance(g, (gpd.GeoDataFrame, gpd.GeoSeries)) else gpd.GeoSeries([g], crs=4326).to_crs(CRS)

def xy(lon, lat):
    x = 6378137.0 * math.radians(lon)
    y = 6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y

# --- Cámara ------------------------------------------------------------------
# (segundo, lon, lat, ancho en grados de longitud)
KEYS = [
    (0.0, -2.0, 46.0, 34.0),   # Europa
    (2.5, -4.0, 39.0, 13.0),   # España
    (6.0, -4.0, 39.0, 12.0),
    (9.0, -5.45, 36.0, 1.5),   # Estrecho
    (13.0, -5.45, 36.0, 1.4),
    (16.0, -5.36, 36.135, 0.13),  # Gibraltar: la cámara se queda aquí hasta el final
    (46.0, -5.352, 36.13, 0.095),
    (52.0, -5.352, 36.13, 0.095),
    (60.0, -5.36, 36.14, 0.16),
]

def ease(u):
    return u * u * (3 - 2 * u)

def camera(t):
    for (t0, x0, y0, w0), (t1, x1, y1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
            # el centro avanza al ritmo del zoom, para que el destino no se salga del encuadre
            k = u if abs(w0 - w1) < 1e-9 else (w0 - w) / (w0 - w1)
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, w
    return KEYS[-1][1:]

# --- Textos por escena ----------------------------------------------------------
# (inicio, fin, título, subtítulo)
TITLES = [
    (0.0, 6.0, "¿Un trozo de Reino Unido…", "…pegado a España?"),
    (6.0, 13.0, "Estrecho de Gibraltar", "La puerta del Mediterráneo"),
    (13.0, 22.0, "Gibraltar", "Menos de 7 km²"),
    (22.0, 31.0, "1704", "Una flota angloholandesa\ntoma el peñón"),
    (31.0, 40.0, "1713 · Tratado de Utrecht", "Cedido a Gran Bretaña\n«para siempre»"),
    (40.0, 46.0, "1967 · Referéndum", "Votan seguir siendo británicos"),
    (46.0, 52.0, "1969 – 1985", "España cierra la frontera"),
    (52.0, 60.0, "Julio de 2026", "Acuerdo UE – Reino Unido:\nadiós a la verja"),
]
# (inicio, fin, lon, lat, texto, tamaño, color)
LABELS = [
    (0.0, 6.0, -3.7, 40.0, "ESPAÑA", 46, INK),
    (9.0, 13.0, -5.3, 36.55, "ESPAÑA", 40, INK),
    (9.0, 13.0, -5.55, 35.25, "MARRUECOS", 36, "white"),
    (9.0, 13.0, -6.05, 35.8, "Océano\nAtlántico", 30, "#8FB3D9"),
    (9.0, 13.0, -4.98, 35.95, "Mar\nMediterráneo", 30, "#8FB3D9"),
    (9.0, 13.0, -5.13, 36.14, "← Gibraltar", 30, "white"),
    (9.0, 13.0, -5.13, 35.80, "Ceuta (España)", 24, "white"),
    (16.0, 60.0, -5.322, 36.122, "GIBRALTAR\n(Reino Unido)", 30, "white"),
    (16.0, 60.0, -5.345, 36.175, "ESPAÑA", 40, INK),
    (16.0, 60.0, -5.352, 36.161, "La Línea", 24, INK),
    (16.0, 60.0, -5.383, 36.105, "Bahía de\nAlgeciras", 24, "#8FB3D9"),
]

def verja_alpha(t):
    if 46.0 <= t < 52.0:
        return 1.0
    if 52.0 <= t < 56.0:
        return 1.0 - (t - 52.0) / 4.0
    return 0.0

# --- Dibujo ----------------------------------------------------------------------
fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)

seam = STRAIT.exterior.buffer(0.002)
P(world).plot(ax=ax, color=LAND, edgecolor=LAND, linewidth=0.6)
P(world[world.ADM0_A3 == "GBR"]).plot(ax=ax, color=UK, linewidth=0)
P(world[world.ADM0_A3 == "ESP"]).plot(ax=ax, color=ESP, edgecolor=ESP, linewidth=0.6)
P(world[world.ADM0_A3 != "ESP"].boundary.difference(seam)).plot(ax=ax, color=BORDER, linewidth=0.8)
P(world[world.ADM0_A3 == "ESP"].boundary.difference(seam)).plot(ax=ax, color="#8A6A00", linewidth=1.2)
P(lakes).plot(ax=ax, color="#3E7CB1", linewidth=0)
# Rellenos sin borde; los contornos se dibujan aparte, sin el corte rectangular de STRAIT
P(mar_d).plot(ax=ax, color=LAND, edgecolor=LAND, linewidth=0.6)
P(esp_d).plot(ax=ax, color=ESP, edgecolor=ESP, linewidth=0.6)
P(mar_d.boundary.difference(seam)).plot(ax=ax, color=BORDER, linewidth=0.8)
P(esp_d.boundary.difference(seam)).plot(ax=ax, color="#8A6A00", linewidth=1.2)
P(gib_d).plot(ax=ax, color=GIB, edgecolor="white", linewidth=2.5)
P(verja).plot(ax=ax, color="#FF2E2E", linewidth=10, zorder=8)
verja_artist = ax.collections[-1]

stroke = lambda w: [pe.withStroke(linewidth=w, foreground=INK)]
t_title = fig.text(0.5, 0.925, "", fontsize=60, color="white", weight="bold", ha="center", va="center", path_effects=stroke(10))
t_sub = fig.text(0.5, 0.865, "", fontsize=36, color="#F2E6C9", ha="center", va="center", path_effects=stroke(7), linespacing=1.2)
fig.text(0.5, 0.03, "Mapas: Natural Earth · geoBoundaries (IGN, CC BY 4.0; OSM, ODbL)", fontsize=18,
         color="white", ha="center", path_effects=stroke(4))
label_artists = []
for (a, b, lon, lat, text, size, color) in LABELS:
    x, y = xy(lon, lat)
    art = ax.text(x, y, text, fontsize=size, color=color, weight="bold", ha="center", va="center", zorder=10,
                  linespacing=1.1, path_effects=stroke(6) if color != INK else [])
    label_artists.append((a, b, art))

def state(t):
    cx, cy, w = camera(t)
    title = next(((ti, su) for a, b, ti, su in TITLES if a <= t < b), TITLES[-1][2:])
    labels = tuple(a <= t < b for a, b, _ in label_artists)
    return (round(cx, 5), round(cy, 5), round(w, 5)), title, labels, round(verja_alpha(t), 2)

def fit(art, text, size):
    """Ajusta el tamaño de letra para que el texto quepa en el 90 % del ancho."""
    art.set_text(text); art.set_fontsize(size)
    r = fig.canvas.get_renderer()
    wpx = art.get_window_extent(r).width
    if wpx > 0.9 * 1080:
        art.set_fontsize(size * 0.9 * 1080 / wpx)

def draw(st):
    (cx, cy, w), (title, sub), labels, alpha = st
    x0, y = xy(cx - w / 2, cy); x1, _ = xy(cx + w / 2, cy)
    h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(y - h / 2, y + h / 2)
    fit(t_title, title, 60); fit(t_sub, sub, 36)
    for vis, (_, _, art) in zip(labels, label_artists):
        art.set_visible(vis)
    verja_artist.set_alpha(alpha); verja_artist.set_visible(alpha > 0)

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
    owner, jobs = [], []  # owner[i] = fotograma que se dibuja y se copia en i
    for i, st in enumerate(states):
        if i and st == states[i - 1]:
            owner.append(owner[-1])
        else:
            owner.append(i); jobs.append((st, FRAMES / f"{i:05d}.png"))
    print(f"{len(jobs)} fotogramas únicos de {n}", flush=True)
    with mp.get_context("fork").Pool(4) as pool:
        for k, _ in enumerate(pool.imap_unordered(render, jobs, chunksize=8)):
            if k % 100 == 0:
                print(f"{k}/{len(jobs)}", flush=True)
    for i, o in enumerate(owner):
        if o != i:
            shutil.copyfile(FRAMES / f"{o:05d}.png", FRAMES / f"{i:05d}.png")

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "gibraltar_short.mp4")], check=True)
    for sec, name in [(1, "01_europa"), (10, "02_estrecho"), (18, "03_gibraltar"), (49, "04_frontera_cerrada"), (58, "05_sin_verja")]:
        shutil.copyfile(FRAMES / f"{sec * FPS:05d}.png", OUT / f"{name}.png")
    shutil.rmtree(FRAMES)
    print("ok")
