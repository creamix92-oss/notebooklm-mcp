import sys
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from shapely.geometry import box, Point

NE = Path(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
CRS = "EPSG:3857"

OCEAN, LAND, BORDER = "#16324F", "#D9D2C3", "#7A7468"
BOL, CHL, PER, LAKE, RIVER = "#F2B632", "#C8553D", "#8FA9A3", "#3E7CB1", "#5FA8E0"

world = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson", columns=["ADM0_A3", "NAME_ES", "geometry"])
adm1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson", columns=["name", "adm0_a3", "geometry"])
lakes = gpd.read_file(NE / "ne_10m_lakes.geojson", columns=["name", "geometry"])
rivers = gpd.read_file(NE / "ne_10m_rivers_lake_centerlines.geojson", columns=["name", "geometry"])

# Litoral boliviano antes de 1879 (aproximado): región de Antofagasta al norte del paralelo 24° S (tratado de 1874)
antof = adm1[(adm1.adm0_a3 == "CHL") & (adm1.name == "Antofagasta")]
litoral = gpd.GeoDataFrame(geometry=[antof.union_all().intersection(box(-75, -24, -60, -15))], crs=4326)
# Tarapacá y Arica eran peruanos en 1879
peru_sur = adm1[(adm1.adm0_a3 == "CHL") & adm1.name.isin(["Tarapacá", "Arica y Parinacota"])]

def P(g):
    return g.to_crs(CRS)

def canvas(lon0, lon1, lat_c):
    """Figura 1080x1920 (9:16) centrada en lat_c, con ancho en longitudes lon0..lon1."""
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    fig.patch.set_facecolor(OCEAN); ax.set_facecolor(OCEAN)
    pts = gpd.GeoSeries([Point(lon0, lat_c), Point(lon1, lat_c)], crs=4326).to_crs(CRS)
    x0, x1 = pts.iloc[0].x, pts.iloc[1].x
    yc = pts.iloc[0].y; h = (x1 - x0) * 16 / 9
    ax.set_xlim(x0, x1); ax.set_ylim(yc - h / 2, yc + h / 2)
    return fig, ax

def base(ax, bolivia_color=BOL):
    P(world).plot(ax=ax, color=LAND, edgecolor=BORDER, linewidth=0.8)
    P(world[world.ADM0_A3 == "PER"]).plot(ax=ax, color=PER, edgecolor=BORDER, linewidth=0.8)
    P(world[world.ADM0_A3 == "CHL"]).plot(ax=ax, color=CHL, edgecolor=BORDER, linewidth=0.8)
    P(world[world.ADM0_A3 == "BOL"]).plot(ax=ax, color=bolivia_color, edgecolor="#5C4A12", linewidth=1.6)

def lakes_layer(ax, lw=0.5):
    P(lakes).plot(ax=ax, color=LAKE, edgecolor="#2A5A85", linewidth=lw)

def label(ax, lon, lat, text, size=34, color="white", weight="bold", stroke=6, **kw):
    p = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(CRS).iloc[0]
    ax.text(p.x, p.y, text, fontsize=size, color=color, weight=weight, ha="center", va="center",
            path_effects=[pe.withStroke(linewidth=stroke, foreground="#0B1A2A")], zorder=10, **kw)

def dot(ax, lon, lat, s=180):
    p = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(CRS).iloc[0]
    ax.scatter([p.x], [p.y], s=s, color="white", edgecolor="#0B1A2A", linewidth=3, zorder=9)

def title(fig, text, sub=None):
    fig.text(0.5, 0.93, text, fontsize=58, color="white", weight="bold", ha="center",
             path_effects=[pe.withStroke(linewidth=10, foreground="#0B1A2A")])
    if sub:
        fig.text(0.5, 0.895, sub, fontsize=32, color="#F2E6C9", ha="center",
                 path_effects=[pe.withStroke(linewidth=6, foreground="#0B1A2A")])

def note(fig, text):
    fig.text(0.5, 0.035, text, fontsize=20, color="white", ha="center", path_effects=[pe.withStroke(linewidth=5, foreground="#0B1A2A")])

def save(fig, name):
    fig.savefig(OUT / name, dpi=100, facecolor=fig.get_facecolor()); plt.close(fig)

SRC = "Mapa: Natural Earth (dominio público)"

# 1. Gancho: Sudamérica
fig, ax = canvas(-84, -32, -22)
base(ax); lakes_layer(ax, 0.2)
label(ax, -64.8, -16.8, "BOLIVIA", size=30, color="#0B1A2A", stroke=0)
label(ax, -86 + 9, -30, "OCÉANO\nPACÍFICO", size=30, color="#8FB3D9", weight="normal", stroke=0)
title(fig, "Sin mar…", "¿y con Armada?")
note(fig, SRC)
save(fig, "01_gancho_sudamerica.png")

# 2. Bolivia en 1879 con su litoral
fig, ax = canvas(-76, -56, -19)
base(ax)
P(peru_sur).plot(ax=ax, color=PER, edgecolor=BORDER, linewidth=0.8)
P(litoral).plot(ax=ax, color=BOL, edgecolor="#5C4A12", linewidth=1.6)
P(world[world.ADM0_A3 == "BOL"]).plot(ax=ax, color=BOL, edgecolor=BOL, linewidth=2)  # funde frontera Bolivia-Litoral
lakes_layer(ax)
label(ax, -64.5, -16.5, "BOLIVIA", size=46, color="#0B1A2A", stroke=0)
label(ax, -73.5, -12.5, "PERÚ", size=38)
label(ax, -71.0, -28.5, "CHILE", size=38)
label(ax, -68.9, -22.9, "LITORAL", size=30, color="#0B1A2A", stroke=0, rotation=80)
dot(ax, -70.40, -23.65); label(ax, -73.6, -23.65, "Antofagasta", size=28)
label(ax, -74.0, -19.5, "OCÉANO\nPACÍFICO", size=28, color="#8FB3D9", weight="normal", stroke=0)
title(fig, "1879", "Bolivia tenía costa")
note(fig, "Fronteras de 1879 aproximadas · " + SRC)
save(fig, "02_bolivia_1879.png")

# 3. Hoy: el litoral es chileno
fig, ax = canvas(-76, -56, -19)
base(ax); lakes_layer(ax)
P(litoral).boundary.plot(ax=ax, color="white", linewidth=4, linestyle=(0, (4, 3)), zorder=8)
label(ax, -64.5, -16.5, "BOLIVIA", size=46, color="#0B1A2A", stroke=0)
label(ax, -73.5, -12.5, "PERÚ", size=38)
label(ax, -71.0, -28.5, "CHILE", size=38)
label(ax, -73.9, -23.0, "Costa\nperdida", size=30)
dot(ax, -70.40, -23.65)
label(ax, -74.0, -19.0, "OCÉANO\nPACÍFICO", size=28, color="#8FB3D9", weight="normal", stroke=0)
title(fig, "Tratado de 1904", "La costa pasa a Chile")
note(fig, "Contorno del litoral aproximado · " + SRC)
save(fig, "03_hoy_sin_costa.png")

# 4. Zoom al Titicaca
fig, ax = canvas(-71.6, -67.6, -16.0)
base(ax); lakes_layer(ax, 1.0)
P(world[world.ADM0_A3.isin(["BOL", "PER"])]).boundary.plot(ax=ax, color="#0B1A2A", linewidth=2.5)
label(ax, -69.40, -15.75, "Lago\nTiticaca", size=40)
label(ax, -68.25, -16.9, "BOLIVIA", size=42, color="#0B1A2A", stroke=0)
label(ax, -70.9, -15.0, "PERÚ", size=40)
dot(ax, -68.15, -16.50); label(ax, -68.15, -16.68, "La Paz", size=28)
title(fig, "Lago Titicaca", "El lago navegable más alto del mundo")
note(fig, SRC)
save(fig, "04_titicaca.png")

# 5. Ríos navegables de Bolivia
bol = world[world.ADM0_A3 == "BOL"]
riv = gpd.clip(rivers[rivers.name.isin(["Mamoré", "Beni", "Guaporé", "Madre de Dios", "Madeira", "Paraguay", "Ichilo", "Yapacani", "Itenez"])], box(-71, -23, -57, -9))
fig, ax = canvas(-72, -56, -16.5)
base(ax); lakes_layer(ax)
P(riv).plot(ax=ax, color=RIVER, linewidth=4.5, zorder=6)
for lon, lat, t in [(-65.1, -13.0, "Mamoré"), (-67.4, -12.6, "Beni"), (-61.6, -13.2, "Guaporé")]:
    label(ax, lon, lat, t, size=26)
label(ax, -69.40, -15.75, "Titicaca", size=26)
label(ax, -63.5, -18.8, "BOLIVIA", size=46, color="#0B1A2A", stroke=0)
title(fig, "La Armada patrulla", "ríos y lagos")
note(fig, SRC)
save(fig, "05_rios_y_lagos.png")
print("ok")
