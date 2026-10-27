"""Vídeo vertical (1080x1920) «¿Sabías que…? Los mapas te mienten».

El mapa del mundo se transforma en directo entre la proyección Mercator y la Equal Earth, se arrastran países
por la esfera para ver su tamaño real y cada curiosidad tiene su propia capa (Bir Tawil, Agloe, Montes Kong…).

Uso: python3 video.py <carpeta_datos> <tiempos.json> <carpeta_salida> [segundos,de,vista,previa]
Datos: Natural Earth (dominio público): países 50m, áreas en disputa 10m y estados 10m.
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
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escenas import SCENES  # noqa: E402

DATA, TIEMPOS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FRAMES = OUT / "frames"
FPS = 24
TT = json.loads(TIEMPOS.read_text())
ESC = TT["escenas"]
DURATION = TT["total"]

OCEAN, LAND, INK, AMBAR = "#0E2A47", "#CFC7B4", "#07131F", "#FFC400"
R = 6378137.0

# --- Proyecciones ---------------------------------------------------------------------------------------------
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
K_EA = A1 * math.sqrt(3) / 2  # iguala el ancho del ecuador de Equal Earth con el de Mercator

def merc(lon, lat):
    lat = np.clip(lat, -85.0, 85.0)
    return R * np.radians(lon), R * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))

def equal_earth(lon, lat):
    lam, phi = np.radians(lon), np.radians(lat)
    th = np.arcsin(math.sqrt(3) / 2 * np.sin(phi))
    x = 2 * math.sqrt(3) * lam * np.cos(th) / (3 * (9 * A4 * th ** 8 + 7 * A3 * th ** 6 + 3 * A2 * th ** 2 + A1))
    y = th * (A1 + A2 * th ** 2 + th ** 6 * (A3 + A4 * th ** 2))
    return R * K_EA * x, R * K_EA * y

def proj(lon, lat, m):
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    if m <= 0:
        return merc(lon, lat)
    if m >= 1:
        return equal_earth(lon, lat)
    (xa, ya), (xb, yb) = merc(lon, lat), equal_earth(lon, lat)
    return (1 - m) * xa + m * xb, (1 - m) * ya + m * yb

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

# --- Datos ----------------------------------------------------------------------------------------------------
def anillos(geom):
    geoms = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    return [np.array(g.exterior.coords) for g in geoms if g.geom_type == "Polygon"]

mundo = gpd.read_file(DATA / "ne_50m_admin_0_countries.geojson", columns=["ADM0_A3", "CONTINENT", "geometry"])
mundo = mundo[mundo.CONTINENT != "Antarctica"]
R_LON, R_LAT, R_ISO, R_CONT, FINES, n = [], [], [], [], [], 0
for fila in mundo.itertuples():
    for a in anillos(fila.geometry):
        R_LON.append(a[:, 0]); R_LAT.append(a[:, 1]); R_ISO.append(fila.ADM0_A3); R_CONT.append(fila.CONTINENT)
        n += len(a); FINES.append(n)
LON, LAT = np.concatenate(R_LON), np.concatenate(R_LAT)
CORTES = FINES[:-1]

def versos(m):
    x, y = proj(LON, LAT, m)
    return np.split(np.column_stack([x, y]), CORTES)

def color_pais(esc, iso, cont):
    c = SCENES[esc]["colores"]
    return to_rgba(c.get(iso) or c.get("@" + cont) or LAND)

COLORES_ESC = [[color_pais(i, iso, cont) for iso, cont in zip(R_ISO, R_CONT)] for i in range(len(SCENES))]

# Groenlandia (arrastre) y centro de África
def vectores(lon, lat):
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])

def a_lonlat(v):
    return np.degrees(np.arctan2(v[:, 1], v[:, 0])), np.degrees(np.arcsin(np.clip(v[:, 2], -1, 1)))

def centro(mask):
    v = vectores(LON[mask], LAT[mask]).mean(axis=0)
    return v / np.linalg.norm(v)

ISO_PTS = np.concatenate([[iso] * len(a) for iso, a in zip(R_ISO, R_LON)])
CONT_PTS = np.concatenate([[c] * len(a) for c, a in zip(R_CONT, R_LON)])
GRL_RINGS = [(a, b) for iso, a, b in zip(R_ISO, R_LON, R_LAT) if iso == "GRL"]
V_GRL = centro(ISO_PTS == "GRL")
V_AFR = centro(CONT_PTS == "Africa")

def rotar(v, eje, ang):
    c, s = math.cos(ang), math.sin(ang)
    return v * c + np.cross(eje, v) * s + np.outer(v @ eje, eje) * (1 - c)

# Capas especiales
disp = gpd.read_file(DATA / "ne_10m_admin_0_disputed_areas.geojson", columns=["NAME", "geometry"])
BIR = {fila.NAME: anillos(fila.geometry) for fila in disp.itertuples() if fila.NAME in ("Bir Tawil", "Halayib Triangle")}

NOMBRES_ESTADOS = ["New York", "California", "Baja California", "Baja California Sur"]
try:
    est = gpd.read_file(DATA / "ne_10m_admin_1_states_provinces.geojson", columns=["name", "geometry"],
                        where="name IN ('New York','California','Baja California','Baja California Sur')")
except Exception:
    est = gpd.read_file(DATA / "ne_10m_admin_1_states_provinces.geojson", columns=["name", "geometry"])
est = est[est.name.isin(NOMBRES_ESTADOS)].copy()
est["geometry"] = est.geometry.simplify(0.003)
ESTADOS = {}
for fila in est.itertuples():
    ESTADOS.setdefault(fila.name, []).extend(anillos(fila.geometry))

# --- Cámara y proyección en el tiempo --------------------------------------------------------------------
def inicio_frase(i, j):
    return ESC[i]["frases"][j][0]

claves = []
for i, sc in enumerate(SCENES):
    for j, fr in enumerate(sc["frases"]):
        if fr.get("cam"):
            claves.append((0.0 if not claves else max(inicio_frase(i, j) - 0.12, 0.0), fr["cam"]))

EVENTOS_MORPH = []
for i, sc in enumerate(SCENES):
    if sc.get("morph"):
        j, objetivo, dur = sc["morph"]
        EVENTOS_MORPH.append((inicio_frase(i, j), objetivo, dur))

def morph(t):
    m = 0.0
    for ts, objetivo, dur in EVENTOS_MORPH:
        if t < ts:
            break
        u = ease((t - ts) / dur)
        if u >= 1:
            m = objetivo
        else:
            m = m + (objetivo - m) * u
            break
    return m

def camara(t):
    k = max(i for i, (kt, _) in enumerate(claves) if kt <= t) if t >= claves[0][0] else 0
    lon1, lat1, w1 = claves[k][1]
    if k == 0:
        lon, lat, w = lon1, lat1, w1
    else:
        kt = claves[k][0]
        lon0, lat0, w0 = claves[k - 1][1]
        d = math.hypot((lon1 - lon0) * math.cos(math.radians((lat0 + lat1) / 2)), lat1 - lat0) / max(w0, w1)
        mov = min(max(0.9 + 0.35 * d, 1.0), 2.2)
        if k + 1 < len(claves):
            mov = min(mov, max(claves[k + 1][0] - kt - 0.2, 0.5))
        u = ease((t - kt) / mov)
        lon, lat = lon0 + (lon1 - lon0) * u, lat0 + (lat1 - lat0) * u
        w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
        w *= 1 + min(1.0, 0.3 * d) * math.sin(math.pi * u)
    w *= 1 + 0.01 * math.sin(0.45 * t)
    lon += 0.005 * w * math.sin(0.7 * t)
    lat += 0.003 * w * math.sin(0.53 * t + 1.0)
    return lon, lat, w

def escena_y_frase(t):
    for i, e in enumerate(ESC):
        if e["inicio"] <= t < e["fin"]:
            for j, (a, b) in enumerate(e["frases"]):
                if a <= t < b:
                    return i, j
            return i, len(e["frases"]) - 1
    return len(ESC) - 1, len(ESC[-1]["frases"]) - 1

# --- Lienzo -------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)
stroke = lambda w, c=INK: [pe.withStroke(linewidth=w, foreground=c)]

paises = PolyCollection(versos(0.0), facecolors=COLORES_ESC[0], edgecolors=(1, 1, 1, 0.5), linewidths=0.7, zorder=1)
ax.add_collection(paises)

# Malla de meridianos y paralelos
GRAT = []
for lo in range(-180, 181, 30):
    GRAT.append((np.full(81, float(lo)), np.linspace(-80, 80, 81)))
for la in range(-60, 61, 30):
    GRAT.append((np.linspace(-180, 180, 121), np.full(121, float(la))))
grat = LineCollection([], colors=[(1, 1, 1, 0.35)], linewidths=1.6, zorder=2)
ax.add_collection(grat)

# Círculos de igual tamaño (indicatriz de Tissot)
def circulo(lon0, lat0, radio_km, n=40):
    d, b = radio_km / 6371.0, np.linspace(0, 2 * math.pi, n)
    la1, lo1 = math.radians(lat0), math.radians(lon0)
    la2 = np.arcsin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * np.cos(b))
    lo2 = lo1 + np.arctan2(np.sin(b) * math.sin(d) * math.cos(la1), math.cos(d) - math.sin(la1) * np.sin(la2))
    return np.degrees(lo2), np.degrees(la2)

TISSOT = [circulo(lo, la, 800) for lo in range(-150, 151, 60) for la in (-60, -30, 0, 30, 60)]
tissot = PolyCollection([], facecolors=[(0.03, 0.07, 0.12, 0.45)], edgecolors=[(1, 1, 1, 0.8)], linewidths=1.6, zorder=3)
ax.add_collection(tissot)

# Arrastre de un país (tamaño real)
arrastre_poly = PolyCollection([], facecolors=[to_rgba("#E4572E", 0.9)], edgecolors=[(1, 1, 1, 1)], linewidths=2.5, zorder=8)
ax.add_collection(arrastre_poly)
arrastre_txt = ax.text(0, 0, "", fontsize=34, color="white", weight="bold", ha="center", va="center", zorder=12,
                       path_effects=stroke(7))

# Capas especiales
bir_poly = {}
for nombre, color in (("Bir Tawil", "#9D8DF1"), ("Halayib Triangle", "#F4B942")):
    pc = PolyCollection([], facecolors=[to_rgba(color, 0.95)], edgecolors=[to_rgba("#FF7B00")], linewidths=3.0, zorder=5)
    ax.add_collection(pc); bir_poly[nombre] = pc
linea_1899 = Line2D([], [], color="white", linewidth=6, zorder=7, path_effects=stroke(11))
ax.add_line(linea_1899)
bir_txt = [ax.text(0, 0, t, fontsize=26, color="white", weight="bold", ha="center", va="center", zorder=12,
                   path_effects=stroke(6)) for t in ("Bir Tawil", "Hala'ib", "frontera de 1899 (22° N)")]

est_poly = {}
for nombre in NOMBRES_ESTADOS:
    pc = PolyCollection([], facecolors=[to_rgba(LAND)], edgecolors=[(1, 1, 1, 0.8)], linewidths=1.5, zorder=4)
    ax.add_collection(pc); est_poly[nombre] = pc
canal = Line2D([], [], color=OCEAN, linewidth=30, solid_capstyle="round", zorder=6)
ax.add_line(canal)
cruce = [Line2D([], [], color=(0.55, 0.55, 0.55), linewidth=16, solid_capstyle="round", zorder=6,
                path_effects=[pe.Stroke(linewidth=18, foreground="white"), pe.Normal()]) for _ in range(2)]
for c in cruce:
    ax.add_line(c)

KONG_PTS = [(lo, 9.2 + 0.9 * math.sin((lo + 11.0) / 17.0 * math.pi)) for lo in np.arange(-11.0, 6.01, 0.45)]
rng = np.random.default_rng(7)
KONG_TAM = rng.uniform(700, 1700, len(KONG_PTS))
KONG_DY = rng.uniform(-0.35, 0.35, len(KONG_PTS))
kong = ax.scatter([], [], s=[], marker="^", color="#8B5E3C", edgecolor="#3A2412", linewidth=2, zorder=6)
kong_txt = ax.text(0, 0, "Montes Kong (inexistentes)", fontsize=30, color="white", weight="bold", ha="center",
                   va="center", zorder=12, path_effects=stroke(7))

america = ax.text(0, 0, "", fontsize=84, color="#F6D58E", family="DejaVu Serif", weight="bold", ha="center",
                  va="center", zorder=12, path_effects=stroke(12), rotation=-12)

# Rutas (rumbo constante y círculo máximo)
def ruta_pts(r, n=140):
    (lo1, la1), (lo2, la2) = r["a"], r["b"]
    if r["tipo"] == "rumbo":
        s = np.linspace(0, 1, n)
        ya = math.log(math.tan(math.pi / 4 + math.radians(la1) / 2))
        yb = math.log(math.tan(math.pi / 4 + math.radians(la2) / 2))
        return lo1 + (lo2 - lo1) * s, np.degrees(np.arctan(np.sinh(ya + (yb - ya) * s)))
    v1, v2 = vectores([lo1], [la1])[0], vectores([lo2], [la2])[0]
    om = math.acos(float(np.clip(v1 @ v2, -1, 1)))
    s = np.linspace(0, 1, n)[:, None]
    v = (np.sin((1 - s) * om) * v1 + np.sin(s * om) * v2) / math.sin(om)
    return a_lonlat(v)

rutas = []
for i, sc in enumerate(SCENES):
    for r in sc.get("rutas", []):
        color = "white" if r["tipo"] == "rumbo" else AMBAR
        ln = Line2D([], [], color=color, linewidth=10, solid_capstyle="round", zorder=9, path_effects=stroke(17))
        ax.add_line(ln)
        lab = ax.text(0, 0, r["texto"], fontsize=28, color=color, weight="bold", ha="center", va="center", zorder=12,
                      path_effects=stroke(7))
        rutas.append((i, r, ruta_pts(r), ln, lab))

# Marcas, pulsos y etiquetas
OFFS = {"arriba": ((0, 24), "center", "bottom"), "abajo": ((0, -24), "center", "top"),
        "der": ((22, 0), "left", "center"), "izq": ((-22, 0), "right", "center")}
marcas, pulsos, etiquetas = [], [], []
for i, sc in enumerate(SCENES):
    for lon, lat, txt, d, desde in sc.get("marcas", []):
        dot = ax.scatter([0], [0], s=240, color="white", edgecolor=INK, linewidth=3, zorder=11)
        off, ha, va = OFFS[d]
        t = ax.annotate(txt, (0, 0), xytext=off, textcoords="offset points", fontsize=28, color="white",
                        weight="bold", ha=ha, va=va, zorder=12, path_effects=stroke(6))
        marcas.append((i, desde, lon, lat, dot, t))
    for lon, lat, desde in sc.get("pulsos", []):
        p = ax.scatter([0], [0], s=100, facecolors="none", edgecolors=AMBAR, linewidths=5, zorder=10)
        pulsos.append((i, desde, lon, lat, p))
    for lon, lat, txt in sc.get("etiquetas", []):
        a = ax.text(0, 0, txt, fontsize=34, color="white", weight="bold", ha="center", va="center", zorder=10,
                    linespacing=1.1, path_effects=stroke(7))
        etiquetas.append((i, lon, lat, a))

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
fig.text(0.5, 0.018, "Mapa: Natural Earth (dominio público) · proyecciones calculadas con fórmulas estándar · posiciones aproximadas",
         fontsize=14, color="white", ha="center", path_effects=stroke(4), zorder=30)

def fit(art, text, size, ancho=0.92):
    art.set_visible(True)
    art.set_text(text); art.set_fontsize(size)
    wpx = art.get_window_extent(fig.canvas.get_renderer()).width
    if wpx > ancho * 1080:
        art.set_fontsize(size * ancho * 1080 / wpx)

M_ULTIMO = [None]

def poner(coll, anillos_ll, m, visible):
    coll.set_visible(visible)
    if visible:
        coll.set_verts([np.column_stack(proj(a[:, 0], a[:, 1], m)) for a in anillos_ll])

def draw(t):
    i, j = escena_y_frase(t)
    sc = SCENES[i]
    m = morph(t)
    # cámara
    lon, lat, w = camara(t)
    cx, cy = proj(lon, lat, m)
    ancho = w * (math.pi * R / 180.0)
    ax.set_xlim(cx - ancho / 2, cx + ancho / 2)
    h = ancho * 16 / 9
    ax.set_ylim(cy - h / 2, cy + h / 2)
    # mundo
    if M_ULTIMO[0] != round(m, 4):
        paises.set_verts(versos(m)); M_ULTIMO[0] = round(m, 4)
    paises.set_facecolor(COLORES_ESC[i])
    grat.set_visible(bool(sc.get("graticula")))
    if sc.get("graticula"):
        grat.set_segments([np.column_stack(proj(a, b, m)) for a, b in GRAT])
    tissot.set_visible(bool(sc.get("tissot")))
    if sc.get("tissot"):
        tissot.set_verts([np.column_stack(proj(a, b, m)) for a, b in TISSOT])
    # arrastre
    ar = sc.get("arrastre")
    arrastre_poly.set_visible(bool(ar)); arrastre_txt.set_visible(bool(ar))
    if ar:
        p = ease((t - inicio_frase(i, ar["desde"])) / ar["dur"]) if j >= ar["desde"] else 0.0
        eje = np.cross(V_GRL, V_AFR); sen = np.linalg.norm(eje); eje = eje / sen
        ang = math.atan2(sen, float(V_GRL @ V_AFR)) * p
        verts = []
        for lo, la in GRL_RINGS:
            lo2, la2 = a_lonlat(rotar(vectores(lo, la), eje, ang))
            verts.append(np.column_stack(proj(lo2, la2, m)))
        arrastre_poly.set_verts(verts)
        c_lo, c_la = a_lonlat(rotar(V_GRL[None, :], eje, ang))
        x, y = proj(c_lo, c_la, m)
        arrastre_txt.set_position((float(x[0]), float(y[0]))); arrastre_txt.set_text(ar["texto"])
    # capas especiales
    bt = bool(sc.get("bir_tawil"))
    for nombre, pc in bir_poly.items():
        poner(pc, BIR.get(nombre, []), m, bt)
    linea_1899.set_visible(bt); [a.set_visible(bt) for a in bir_txt]
    if bt:
        x, y = proj(np.array([30.0, 38.0]), np.array([22.0, 22.0]), m)
        linea_1899.set_data(x, y)
        for a, (lo, la) in zip(bir_txt, ((33.75, 21.62), (35.6, 22.4), (33.3, 22.14))):
            px, py = proj(lo, la, m); a.set_position((float(px), float(py)))
    ed = sc.get("estados", {})
    cal = bool(sc.get("california"))
    for nombre, pc in est_poly.items():
        on = nombre in ed or (cal and nombre in ("California", "Baja California", "Baja California Sur"))
        poner(pc, ESTADOS.get(nombre, []), m, on)
        if on:
            pc.set_facecolor([to_rgba(ed.get(nombre, AMBAR))])
    canal.set_visible(cal)
    if cal:
        x, y = proj(np.array([-114.9, -115.9, -117.6, -119.6, -121.6, -123.8, -124.5]),
                    np.array([31.9, 33.5, 35.1, 37.4, 39.8, 41.8, 43.3]), m)
        canal.set_data(x, y)
        canal.set_alpha(1.0 - ease((t - inicio_frase(i, 2) - 0.2) / 1.5) if j >= 2 else 1.0)
    es_ag = "New York" in ed
    for c, (dx, dy) in zip(cruce, ((0.18, 0.12), (-0.18, 0.12))):
        c.set_visible(es_ag and j >= 4)
        if es_ag:
            x, y = proj(np.array([AGLOE_LON - dx, AGLOE_LON + dx]), np.array([AGLOE_LAT - dy, AGLOE_LAT + dy]), m)
            c.set_data(x, y)
    kg = bool(sc.get("kong"))
    kong.set_visible(kg); kong_txt.set_visible(kg)
    if kg:
        pts = np.array(KONG_PTS)
        x, y = proj(pts[:, 0], pts[:, 1] + KONG_DY, m)
        kong.set_offsets(np.column_stack([x, y]))
        aparece = ease((t - inicio_frase(i, 1)) / 4.0) if j >= 1 else 0.0
        desaparece = ease((t - inicio_frase(i, 3)) / 2.5) if j >= 3 else 0.0
        vis = np.clip((np.linspace(0, 1, len(pts)) <= aparece).astype(float), 0, 1) * (1 - desaparece)
        kong.set_sizes(KONG_TAM * vis * 1.0)
        kong.set_alpha(None)
        kong.set_facecolor([(0.55, 0.37, 0.24, a) for a in vis]); kong.set_edgecolor([(0.23, 0.14, 0.07, a) for a in vis])
        px, py = proj(-2.5, 12.2, m); kong_txt.set_position((float(px), float(py)))
        kong_txt.set_alpha(max(0.0, 1.0 - desaparece) if j >= 1 else 0.0)
    am = bool(sc.get("america"))
    america.set_visible(am)
    if am:
        px, py = proj(-60.0, -2.0, m); america.set_position((float(px), float(py)))
        america.set_text("AMERICA"[: int(7 * ease((t - inicio_frase(i, 0) - 1.0) / 2.2) + 0.01)])
    # rutas
    for (si, r, (lo, la), ln, lab) in rutas:
        v = si == i and j >= r["desde"]
        ln.set_visible(v); lab.set_visible(v and w < 100)
        if v:
            x, y = proj(lo, la, m)
            cum = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
            f = ease((t - inicio_frase(i, r["desde"])) / r["dur"])
            k = int(np.searchsorted(cum, f * cum[-1], side="right"))
            ln.set_data(x[:max(k, 2)], y[:max(k, 2)])
            km = len(x) // 2
            lab.set_position((float(x[km]), float(y[km]) + (1 if r["tipo"] == "rumbo" else -1) * 0.025 * ancho))
            lab.set_alpha(min(1.0, f * 3))
    # marcas, pulsos, etiquetas
    for (si, desde, lo, la, dot, txt) in marcas:
        v = si == i and j >= desde
        dot.set_visible(v); txt.set_visible(v)
        if v:
            x, y = proj(lo, la, m); dot.set_offsets([[float(x), float(y)]]); txt.xy = (float(x), float(y))
    for (si, desde, lo, la, p) in pulsos:
        v = si == i and j >= desde
        p.set_visible(v)
        if v:
            x, y = proj(lo, la, m); p.set_offsets([[float(x), float(y)]])
            ph = (t * 0.9) % 1.0
            p.set_sizes([150 + 3200 * ph]); p.set_alpha(1 - ph)
    for (si, lo, la, a) in etiquetas:
        a.set_visible(si == i)
        if si == i:
            x, y = proj(lo, la, m); a.set_position((float(x), float(y)))
            if sc.get("california"):
                a.set_alpha(1.0 - ease((t - inicio_frase(i, 2)) / 1.5) if j >= 2 else 1.0)
    # textos
    pulso = 1 + 0.045 * math.sin(2 * math.pi * 1.3 * t) if i == 0 else 1.0
    fit(t_title, sc["titulo"], sc.get("titulo_size", 60) * pulso, 0.94)
    fit(t_sub, sc["sub"], 34, 0.94)
    fr = sc["frases"][j]
    fit(t_cap, "\n".join(textwrap.wrap(fr["texto"], 30)), 42, 0.95)
    if fr.get("stat"):
        u = (t - inicio_frase(i, j)) / 0.45
        esc = 0.55 + 0.45 * ease(u) + 0.14 * math.sin(math.pi * min(u, 1.0))
        t_statl.set_visible(True)
        fit(t_stat, fr["stat"][0], 120 * esc, 0.86 * min(1.0, 0.3 + u))
        t_statl.set_text(fr["stat"][1])
    else:
        t_stat.set_visible(False); t_statl.set_visible(False)

AGLOE_LON, AGLOE_LAT = -74.92, 41.99

def render(job):
    n_, f = job
    draw(n_ / FPS); fig.savefig(f, dpi=100, facecolor=OCEAN)
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
    total = int(FPS * DURATION)
    jobs = [(k, FRAMES / f"{k:05d}.png") for k in range(total)]
    print(f"{total} fotogramas", flush=True)
    with mp.get_context("fork").Pool(4) as pool:
        for k, _ in enumerate(pool.imap_unordered(render, jobs, chunksize=6)):
            if k % 300 == 0:
                print(f"{k}/{total}", flush=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT / "video_sin_voz.mp4")], check=True)
    shutil.rmtree(FRAMES)
    print("ok")
