"""Vídeo vertical (1080x1920) «¿Sabías que…? Nueve ríos que unen y separan países de Sudamérica».

Cámara que vuela entre frases, ríos que se dibujan con partículas de agua, pulsos en las triples fronteras,
cifras grandes y subtítulos sincronizados con la narración.

Uso: python3 video.py <carpeta_datos> <tiempos.json> <carpeta_salida> [segundos,de,vista,previa]
Datos: Natural Earth 10m (dominio público).
"""
import json
import math
import multiprocessing as mp
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from shapely.geometry import box, LineString
from shapely.ops import linemerge

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escenas import SCENES, RIOS, NOMBRES, SA  # noqa: E402

DATA, TIEMPOS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FRAMES = OUT / "frames"
FPS, CRS = 24, "EPSG:3857"
TT = json.loads(TIEMPOS.read_text())
ESC = TT["escenas"]
DURATION = TT["total"]

OCEAN, LAND, INK = "#0E2A47", "#CFC7B4", "#07131F"
AGUA, AGUA_CLARA, AMBAR = "#2BB1FF", "#8FE0FF", "#FFC400"

# --- Datos -------------------------------------------------------------------------------------------------
def xy(lon, lat):
    return 6378137.0 * math.radians(lon), 6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

world = gpd.read_file(DATA / "ne_10m_admin_0_countries.geojson", columns=["ADM0_A3", "geometry"])
caja = box(-86, -58, -30, 14)
sa = gpd.clip(world, caja)
sa["geometry"] = sa.geometry.simplify(0.004)
guf = gpd.clip(world[world.ADM0_A3 == "FRA"], box(-55, 1.5, -50.5, 6.5))
guf["ADM0_A3"] = "GUF"
paises = {r.ADM0_A3: r.geometry for r in sa.itertuples() if r.ADM0_A3 != "FRA"}
paises["GUF"] = guf.geometry.iloc[0].simplify(0.004)

rios_ne = gpd.read_file(DATA / "ne_10m_rivers_lake_centerlines.geojson", columns=["name", "geometry"])

def orientar(coords, inicio):
    """Devuelve las coordenadas con el extremo `inicio` (oeste/norte/sur) primero."""
    a, b = coords[0], coords[-1]
    primero = {"oeste": a[0] <= b[0], "norte": a[1] >= b[1], "sur": a[1] <= b[1], None: True}[inicio]
    return coords if primero else coords[::-1]

def partes_rio(cfg):
    if "aprox" in cfg:
        return [[tuple(p) for p in cfg["aprox"]]]
    partes = []
    for fila in rios_ne[rios_ne.name.isin(cfg["ne"])].itertuples():
        geoms = [fila.geometry] if fila.geometry.geom_type == "LineString" else list(fila.geometry.geoms)
        for g in geoms:
            x0, y0, x1, y1 = g.bounds
            if "caja" in cfg:
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                if not (cfg["caja"][0] <= cx <= cfg["caja"][2] and cfg["caja"][1] <= cy <= cfg["caja"][3]):
                    continue
            partes.append(orientar(list(g.coords), cfg.get("inicio")))
    return partes

def a_merc(coords):
    pts = np.array([xy(lon, lat) for lon, lat in coords])
    cum = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return pts[:, 0], pts[:, 1], cum

# --- Cámara --------------------------------------------------------------------------------------------------
def inicio_frase(i, j):
    return ESC[i]["frases"][j][0]

claves = []  # (t, (lon, lat, ancho))
for i, sc in enumerate(SCENES):
    for j, fr in enumerate(sc["frases"]):
        if fr.get("cam"):
            claves.append((0.0 if not claves else max(inicio_frase(i, j) - 0.12, 0.0), fr["cam"]))

def camara(t):
    k = max(i for i, (kt, _) in enumerate(claves) if kt <= t) if t >= claves[0][0] else 0
    lon1, lat1, w1 = claves[k][1]
    if k == 0:
        lon, lat, w = lon1, lat1, w1
    else:
        kt = claves[k][0]
        lon0, lat0, w0 = claves[k - 1][1]
        d = math.hypot((lon1 - lon0) * math.cos(math.radians((lat0 + lat1) / 2)), lat1 - lat0) / max(w0, w1)
        mov = min(max(0.9 + 0.35 * d, 1.0), 2.0)
        if k + 1 < len(claves):
            mov = min(mov, max(claves[k + 1][0] - kt - 0.2, 0.5))
        u = ease((t - kt) / mov)
        lon, lat = lon0 + (lon1 - lon0) * u, lat0 + (lat1 - lat0) * u
        w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
        w *= 1 + min(1.1, 0.32 * d) * math.sin(math.pi * u)  # se aleja a mitad de vuelo y vuelve a acercarse
    w *= 1 + 0.012 * math.sin(0.45 * t)                      # balanceo suave: el mapa nunca está quieto
    lon += 0.006 * w * math.sin(0.7 * t)
    lat += 0.004 * w * math.sin(0.53 * t + 1.0)
    return lon, lat, w

def escena_y_frase(t):
    for i, e in enumerate(ESC):
        if e["inicio"] <= t < e["fin"]:
            for j, (a, b) in enumerate(e["frases"]):
                if a <= t < b:
                    return i, j
            return i, len(e["frases"]) - 1
    return len(ESC) - 1, len(ESC[-1]["frases"]) - 1

# --- Dibujo ----------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)
stroke = lambda w, c=INK: [pe.withStroke(linewidth=w, foreground=c)]

art_pais = {}
for iso, geom in paises.items():
    gpd.GeoSeries([geom], crs=4326).to_crs(CRS).plot(ax=ax, color=LAND, edgecolor=(1, 1, 1, 0.55), linewidth=0.9)
    art_pais[iso] = ax.collections[-1]

# Ríos
art_rio = {}
for key, cfg in RIOS.items():
    partes = [a_merc(p) for p in partes_rio(cfg)]
    glow, core = [], []
    estilo = (0, (2.0, 1.4)) if "aprox" in cfg else "-"
    for _ in partes:
        g = Line2D([], [], color=INK, linewidth=13, alpha=0.0, solid_capstyle="round", zorder=5)
        c = Line2D([], [], color=AGUA_CLARA, linewidth=7, alpha=0.0, linestyle=estilo, solid_capstyle="round", zorder=6)
        ax.add_line(g); ax.add_line(c); glow.append(g); core.append(c)
    parts_geo = partes_rio(cfg)
    art_rio[key] = dict(partes=partes, glow=glow, core=core, particulas=ax.scatter([], [], s=90, color="white", zorder=7, edgecolor=INK, linewidth=2))

# Eventos de revelado de cada río: primera aparición (escena, frase, duración)
reveal = {}
for i, sc in enumerate(SCENES):
    for key, j, dur in sc.get("rios", []):
        reveal.setdefault(key, (i, j, dur))

# Fantasma que se mueve (Pilcomayo)
ghost = [Line2D([], [], color="white", linewidth=6, alpha=0.0, zorder=6, solid_capstyle="round") for _ in range(4)]
for g in ghost:
    ax.add_line(g)

# Marcadores, pulsos, flechas, medidas y rótulos de país por escena
OFFS = {"arriba": ((0, 24), "center", "bottom"), "abajo": ((0, -24), "center", "top"),
        "der": ((22, 0), "left", "center"), "izq": ((-22, 0), "right", "center")}
marcas, pulsos, flechas, medidas, nombres_art = [], [], [], [], []
for i, sc in enumerate(SCENES):
    for lon, lat, txt, d, desde in sc.get("marcas", []):
        x, y = xy(lon, lat)
        dot = ax.scatter([x], [y], s=240, color="white", edgecolor=INK, linewidth=3, zorder=11)
        off, ha, va = OFFS[d]
        t = ax.annotate(txt, (x, y), xytext=off, textcoords="offset points", fontsize=28, color="white",
                        weight="bold", ha=ha, va=va, zorder=12, path_effects=stroke(6))
        marcas.append((i, desde, dot, t))
    for lon, lat, desde in sc.get("pulsos", []):
        x, y = xy(lon, lat)
        p = ax.scatter([x], [y], s=100, facecolors="none", edgecolors=AMBAR, linewidths=5, zorder=10)
        pulsos.append((i, desde, p))
    for fl in sc.get("flechas", []):
        pts = a_merc(fl["pts"])
        ls = (0, (1.6, 1.1)) if fl.get("dash") else "-"
        line = Line2D([], [], color="white", linewidth=10, linestyle=ls, solid_capstyle="round", zorder=9,
                      path_effects=stroke(16))
        head = FancyArrowPatch((0, 0), (1, 1), arrowstyle="-|>,head_length=30,head_width=17", mutation_scale=1,
                               color="white", linewidth=2, zorder=9)
        ax.add_line(line); ax.add_patch(head)
        lab = None
        if fl.get("texto"):
            lab = ax.annotate(fl["texto"], (pts[0][-1], pts[1][-1]), xytext=(0, 22), textcoords="offset points",
                              fontsize=28, color="white", weight="bold", ha="center", va="bottom", zorder=12,
                              path_effects=stroke(6))
        flechas.append((i, fl, pts, line, head, lab))
    for md in sc.get("medidas", []):
        (xa, ya), (xb, yb) = xy(*md["pts"][0]), xy(*md["pts"][1])
        arr = FancyArrowPatch((xa, ya), (xb, yb), arrowstyle="<|-|>,head_length=20,head_width=10", mutation_scale=1,
                              color=AMBAR, linewidth=7, zorder=9)
        ax.add_patch(arr)
        lab = ax.text((xa + xb) / 2, (ya + yb) / 2, md["texto"], fontsize=34, color=AMBAR, weight="bold",
                      ha="center", va="bottom", zorder=12, path_effects=stroke(7), rotation=0)
        medidas.append((i, md["from_idx"], arr, lab))
    for iso in sc.get("nombres", {}):
        lon, lat, txt = NOMBRES[iso]
        pos = sc["nombres"][iso]
        if pos:
            lon, lat = pos
        x, y = xy(lon, lat)
        a = ax.text(x, y, txt, fontsize=36, color="white", weight="bold", ha="center", va="center", zorder=10,
                    linespacing=1.1, path_effects=stroke(7))
        nombres_art.append((i, iso, a))

t_title = fig.text(0.5, 0.925, "", fontsize=60, color="white", weight="bold", ha="center", va="center",
                   path_effects=stroke(10), zorder=30)
t_sub = fig.text(0.5, 0.865, "", fontsize=34, color="#F2E6C9", ha="center", va="center", path_effects=stroke(7),
                 zorder=30)
t_stat = fig.text(0.5, 0.385, "", fontsize=120, color=AMBAR, weight="bold", ha="center", va="center",
                  path_effects=stroke(14), zorder=30)
t_statl = fig.text(0.5, 0.325, "", fontsize=38, color="white", weight="bold", ha="center", va="center",
                   path_effects=stroke(8), zorder=30)
t_cap = fig.text(0.5, 0.05, "", fontsize=42, color="white", weight="bold", ha="center", va="bottom",
                 linespacing=1.25, path_effects=stroke(11), zorder=30)
fig.text(0.5, 0.018, "Mapa: Natural Earth (dominio público) · Lugares y rutas aproximados · línea discontinua: trazado aproximado",
         fontsize=14, color="white", ha="center", path_effects=stroke(4), zorder=30)

def fit(art, text, size, ancho=0.92):
    art.set_text(text); art.set_fontsize(size)
    wpx = art.get_window_extent(fig.canvas.get_renderer()).width
    if wpx > ancho * 1080:
        art.set_fontsize(size * ancho * 1080 / wpx)

def parcial(xs, ys, cum, frac):
    d = frac * cum[-1]
    n = int(np.searchsorted(cum, d, side="right"))
    if n >= len(cum):
        return xs, ys
    u = (d - cum[n - 1]) / (cum[n] - cum[n - 1]) if cum[n] > cum[n - 1] else 0.0
    return (np.append(xs[:n], xs[n - 1] + (xs[n] - xs[n - 1]) * u), np.append(ys[:n], ys[n - 1] + (ys[n] - ys[n - 1]) * u))

def frac_rio(key, t):
    if key not in reveal:
        return 0.0
    i, j, dur = reveal[key]
    return ease((t - inicio_frase(i, j)) / dur)

def draw(t):
    i, j = escena_y_frase(t)
    sc = SCENES[i]
    # cámara
    lon, lat, w = camara(t)
    x0, y = xy(lon - w / 2, lat); x1, _ = xy(lon + w / 2, lat)
    cy = xy(lon, lat)[1]
    h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(cy - h / 2, cy + h / 2)
    # países
    for iso, art in art_pais.items():
        art.set_facecolor(sc["colores"].get(iso, LAND))
    # ríos
    todos = sc.get("todos_los_rios", False)
    en_escena = {k for k, _, _ in sc.get("rios", [])}
    for key, art in art_rio.items():
        f = frac_rio(key, t)
        resaltado = todos or (key in en_escena and f > 0)
        alpha = 1.0 if resaltado else 0.42
        for (xs, ys, cum), g, c in zip(art["partes"], art["glow"], art["core"]):
            if f <= 0:
                g.set_alpha(0); c.set_alpha(0); continue
            px, py = parcial(xs, ys, cum, f)
            g.set_data(px, py); c.set_data(px, py)
            g.set_alpha(0.6 * alpha); c.set_alpha(alpha)
        if resaltado and f > 0.02:
            pts = []
            for xs, ys, cum in art["partes"]:
                for k in range(7):
                    s = ((t * 0.11) + k / 7) % 1.0 * f
                    d = s * cum[-1]
                    n = int(np.searchsorted(cum, d, side="right"))
                    if 0 < n < len(cum):
                        u = (d - cum[n - 1]) / (cum[n] - cum[n - 1]) if cum[n] > cum[n - 1] else 0.0
                        pts.append((xs[n - 1] + (xs[n] - xs[n - 1]) * u, ys[n - 1] + (ys[n] - ys[n - 1]) * u))
            art["particulas"].set_offsets(np.array(pts) if pts else np.empty((0, 2)))
        else:
            art["particulas"].set_offsets(np.empty((0, 2)))
    # río fantasma que se mueve (Pilcomayo)
    wg = sc.get("wiggle")
    activo = bool(wg) and wg[1] <= j <= (wg[2] if wg[2] is not None else 99)
    if activo:
        xs, ys, cum = art_rio[wg[0]]["partes"][0]
        pasos = (cum / cum[-1])
        for k, g in enumerate(ghost):
            amp = 17000 * (0.5 + 0.5 * k / 3)
            off = amp * np.sin(pasos * 40 + t * (1.3 + 0.35 * k) + k * 1.7) * np.minimum(1, pasos * 6)
            g.set_data(xs, ys + off); g.set_alpha(0.9 - 0.15 * k)
    else:
        for g in ghost:
            g.set_alpha(0)
    # marcas, pulsos, flechas, medidas, nombres
    for (si, desde, dot, txt) in marcas:
        v = si == i and j >= desde
        dot.set_visible(v); txt.set_visible(v)
    for (si, desde, p) in pulsos:
        v = si == i and j >= desde
        p.set_visible(v)
        if v:
            ph = (t * 0.9) % 1.0
            p.set_sizes([150 + 3200 * ph]); p.set_alpha(1 - ph)
    for (si, fl, pts, line, head, lab) in flechas:
        v = si == i and j >= fl["from_idx"]
        line.set_visible(v); head.set_visible(v)
        if lab:
            lab.set_visible(v)
        if v:
            f = ease((t - inicio_frase(i, fl["from_idx"])) / fl["dur"])
            px, py = parcial(*pts, f)
            line.set_data(px, py)
            hl = 0.03 * (x1 - x0)
            bx, by = (px[-2], py[-2]) if len(px) > 1 else (px[-1], py[-1])
            L = math.hypot(px[-1] - bx, py[-1] - by) or 1.0
            head.set_positions((px[-1] - (px[-1] - bx) / L * hl, py[-1] - (py[-1] - by) / L * hl), (px[-1], py[-1]))
    for (si, desde, arr, lab) in medidas:
        v = si == i and j >= desde
        arr.set_visible(v); lab.set_visible(v)
    for (si, iso, a) in nombres_art:
        a.set_visible(si == i)
    # textos
    pulso = 1 + 0.045 * math.sin(2 * math.pi * 1.3 * t) if i == 0 else 1.0
    fit(t_title, sc["titulo"], sc.get("titulo_size", 60) * pulso, 0.92)
    fit(t_sub, sc["sub"], 34, 0.92)
    fr = sc["frases"][j]
    fit(t_cap, "\n".join(textwrap.wrap(fr["texto"], 30)), 42, 0.95)
    if fr.get("stat"):
        t_stat.set_visible(True); t_statl.set_visible(True)
        u = (t - inicio_frase(i, j)) / 0.45
        esc = 0.55 + 0.45 * ease(u) + 0.14 * math.sin(math.pi * min(u, 1.0))
        fit(t_stat, fr["stat"][0], 120 * esc, 0.86 * min(1.0, 0.3 + u))
        t_statl.set_text(fr["stat"][1]); t_statl.set_visible(True); t_stat.set_visible(True)
    else:
        t_stat.set_visible(False); t_statl.set_visible(False)

def render(job):
    n, f = job
    draw(n / FPS); fig.savefig(f, dpi=100, facecolor=OCEAN)
    return f

if __name__ == "__main__" and len(sys.argv) > 4:  # vista previa: segundos sueltos
    OUT.mkdir(parents=True, exist_ok=True)
    for sec in sys.argv[4].split(","):
        draw(float(sec)); fig.savefig(OUT / f"preview_{sec}.png", dpi=100, facecolor=OCEAN)
    sys.exit()

if __name__ == "__main__":
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)
    n = int(FPS * DURATION)
    jobs = [(k, FRAMES / f"{k:05d}.png") for k in range(n)]
    print(f"{n} fotogramas", flush=True)
    with mp.get_context("fork").Pool(4) as pool:
        for k, _ in enumerate(pool.imap_unordered(render, jobs, chunksize=6)):
            if k % 300 == 0:
                print(f"{k}/{n}", flush=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "video_sin_voz.mp4")], check=True)
    shutil.rmtree(FRAMES)
    print("ok")
