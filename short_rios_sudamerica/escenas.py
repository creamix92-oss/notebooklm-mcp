"""Escenas de «¿Sabías que…? Nueve ríos que unen y separan países de Sudamérica».

Cada escena: titulo, sub, colores {ISO3: color}, nombres {ISO3: (lon, lat)} y una lista de frases.
Cada frase: texto (se narra y sale como subtítulo), cam=(lon, lat, ancho en grados) opcional (la cámara vuela
hasta ahí al empezar la frase) y stat=(cifra grande, etiqueta) opcional.
Elementos de la escena que aparecen desde una frase (from_idx): marcas, pulsos, rios, flechas, medidas, wiggle.
"""
AMBAR, ROJO, VERDE, VIOLETA, TURQUESA, ROSA = "#F4B942", "#E4572E", "#7FB069", "#9D8DF1", "#4ECDC4", "#FF8FA3"

SA = (-60.0, -20.0, 50.0)

# ---- Lugares (lon, lat); los cruces de fronteras salen de los datos de Natural Earth --------------------------
TRI_COL_BRA_PER = (-69.965, -4.226)
TRI_ARG_BRA_PRY = (-54.594, -25.575)
HITO_ESMERALDA = (-62.649, -22.227)
ITAIPU = (-54.555, -25.444)
LETICIA, TABATINGA = (-69.940, -4.215), (-69.937, -4.253)
CIUDAD_DEL_ESTE, FOZ, PTO_IGUAZU = (-54.611, -25.510), (-54.585, -25.516), (-54.574, -25.599)
CATARATAS = (-54.44, -25.69)
SILALA = (-68.03, -22.03)
OIAPOQUE, SAINT_GEORGES = (-51.835, 3.84), (-51.805, 3.89)
CAYENA, MACAPA = (-52.326, 4.922), (-51.066, 0.035)
PUNTA_DEL_ESTE, PUNTA_RASA = (-54.95, -34.97), (-56.77, -36.32)

# ---- Ríos: ne = nombres en Natural Earth; inicio = extremo por donde empieza a dibujarse (aguas arriba);
# aprox = trazado dibujado a mano (no está en Natural Earth); caja = filtro para elegir el tramo correcto.
RIOS = {
    "amazonas": dict(ne=["Amazonas"], inicio="oeste"),
    "putumayo": dict(ne=["Putumayo"], inicio="oeste"),
    "casiquiare": dict(ne=["Casiquiare"], inicio="norte"),
    "orinoco": dict(ne=["Orinoco"], inicio="sur"),
    "negro": dict(ne=["Negro"], inicio="oeste", caja=(-72, -4, -58, 4)),
    "parana": dict(ne=["Paraná"], inicio="norte"),
    "uruguay": dict(ne=["Uruguay"], inicio="norte"),
    "pilcomayo": dict(ne=["Pilcomayo"], inicio="oeste"),
    "iguazu": dict(aprox=[(-53.65, -25.58), (-54.0, -25.67), (-54.44, -25.69), (-54.59, -25.60)]),
    "paraguay": dict(aprox=[(-57.65, -25.28), (-57.85, -25.75), (-58.0, -26.3), (-58.3, -26.87), (-58.62, -27.32)]),
}

NOMBRES = {  # posición por defecto de los rótulos de país
    "PER": (-75.0, -9.5, "PERÚ"), "COL": (-73.5, 3.5, "COLOMBIA"), "BRA": (-54.0, -10.0, "BRASIL"),
    "ECU": (-78.3, -1.3, "ECUADOR"), "VEN": (-66.0, 7.0, "VENEZUELA"), "ARG": (-65.0, -34.0, "ARGENTINA"),
    "PRY": (-58.4, -23.2, "PARAGUAY"), "BOL": (-64.5, -16.5, "BOLIVIA"), "CHL": (-71.0, -30.0, "CHILE"),
    "URY": (-56.0, -32.8, "URUGUAY"), "GUF": (-53.0, 4.2, "GUAYANA\nFRANCESA"),
}

SCENES = [
    # 0 · Gancho
    dict(titulo="¿SABÍAS QUE…?", sub="9 ríos · 9 fronteras", titulo_size=92,
         colores={"ARG": TURQUESA, "BOL": AMBAR, "PRY": ROJO}, nombres={},
         wiggle=("pilcomayo", 0, 1),
         frases=[
             dict(texto="¿Sabías que en Sudamérica hay un río que cambia tanto de cauce,", cam=(-60.5, -23.8, 13.0)),
             dict(texto="que dos países vecinos tuvieron que firmar tratados para decidir por dónde pasa la frontera?"),
             dict(texto="Te lo cuento al final.", cam=SA),
             dict(texto="Pero antes, nueve historias de ríos que unen, separan, y hasta conectan países enteros.",
                  stat=("9", "historias de ríos")),
             dict(texto="Vamos allá.", cam=(-72.0, -4.0, 20.0)),
         ]),
    # 1 · Amazonas
    dict(titulo="1 · El Amazonas", sub="Perú · Colombia · Brasil",
         colores={"PER": AMBAR, "COL": ROJO, "BRA": VERDE}, nombres={"PER": None, "COL": None, "BRA": None},
         rios=[("amazonas", 0, 7.0)],
         frases=[
             dict(texto="Primero, el gigante: el Amazonas.", cam=(-62.0, -4.0, 24.0)),
             dict(texto="Lleva entre el quince y el veinte por ciento de toda el agua dulce que los ríos del mundo vierten al océano.",
                  cam=(-54.0, -2.0, 10.0), stat=("15–20 %", "del agua dulce que llega al océano")),
             dict(texto="Más de doscientos mil metros cúbicos por segundo, según el promedio más citado.",
                  cam=(-64.0, -3.5, 8.0), stat=("209.000 m³/s", "caudal medio")),
         ]),
    # 2 · Tres Fronteras del Amazonas
    dict(titulo="1 · El Amazonas", sub="Tres países en una ciudad",
         colores={"PER": AMBAR, "COL": ROJO, "BRA": VERDE},
         nombres={"PER": (-70.05, -4.33), "COL": (-70.03, -4.12), "BRA": (-69.84, -4.33)},
         marcas=[(*LETICIA, "Leticia", "arriba", 1), (*TABATINGA, "Tabatinga", "abajo", 1),
                 (*TRI_COL_BRA_PER, "Santa Rosa", "izq", 2)],
         pulsos=[(*TRI_COL_BRA_PER, 2)],
         frases=[
             dict(texto="Y justo en el Amazonas hay un lugar que desafía los mapas.", cam=(-69.95, -4.23, 1.6)),
             dict(texto="Leticia, en Colombia, y Tabatinga, en Brasil, forman un solo núcleo urbano de más de cien mil habitantes.",
                  cam=(-69.94, -4.235, 0.42), stat=("+100.000", "habitantes")),
             dict(texto="Y a un paso, en una isla del río, está Santa Rosa, en Perú.", cam=(-69.96, -4.228, 0.32)),
             dict(texto="Tres países, un mismo río.", cam=(-69.945, -4.235, 0.75)),
             dict(texto="Según las guías de viaje, se puede cruzar a pie entre Leticia y Tabatinga, sin trámites, en visitas cortas.",
                  cam=(-69.945, -4.235, 0.5)),
             dict(texto="Y un detalle: Colombia reclama la isla de Santa Rosa, aunque la administra Perú.",
                  cam=(-69.97, -4.225, 0.26)),
         ]),
    # 3 · Putumayo
    dict(titulo="2 · El Putumayo", sub="Colombia · Ecuador · Perú",
         colores={"COL": ROJO, "ECU": VIOLETA, "PER": AMBAR, "BRA": VERDE},
         nombres={"COL": (-75.0, 2.0), "ECU": (-78.0, -1.0), "PER": (-74.5, -5.5), "BRA": (-67.0, -4.5)},
         rios=[("putumayo", 0, 6.0)],
         frases=[
             dict(texto="Subimos un poco al norte: el río Putumayo.", cam=(-72.5, -1.0, 9.0)),
             dict(texto="Es la frontera entre Colombia y Ecuador, y casi toda la frontera entre Colombia y Perú.",
                  cam=(-73.5, -0.8, 6.5)),
             dict(texto="Al entrar en Brasil cambia de nombre: allí se llama Içá.", cam=(-68.6, -2.8, 5.0)),
             dict(texto="Y según el Museo Field, es una de las pocas cuencas amazónicas sin presas.",
                  cam=(-71.0, -2.0, 12.0), stat=("SIN PRESAS", "una de las pocas cuencas amazónicas")),
         ]),
    # 4 · Casiquiare
    dict(titulo="3 · El Casiquiare", sub="El río que conecta dos mundos",
         colores={"VEN": VIOLETA}, nombres={"VEN": (-66.0, 5.6)},
         rios=[("orinoco", 0, 2.5), ("negro", 0, 2.5), ("casiquiare", 1, 4.5)],
         frases=[
             dict(texto="Ahora, un río que parece imposible: el Casiquiare, en el sur de Venezuela.", cam=(-66.4, 2.5, 4.5)),
             dict(texto="Sale del Alto Orinoco y desemboca en el Río Negro, un afluente del Amazonas.", cam=(-66.4, 2.45, 3.0)),
             dict(texto="Conecta de forma natural dos de las mayores cuencas del planeta: la del Orinoco y la del Amazonas.",
                  cam=(-65.0, 1.8, 16.0)),
             dict(texto="Mide entre trescientos veinte y trescientos cincuenta kilómetros,", cam=(-66.4, 2.5, 4.2),
                  stat=("320–356 km", "de longitud")),
             dict(texto="y se lleva entre el veinticinco y el treinta por ciento del caudal del Alto Orinoco.",
                  stat=("25–30 %", "del caudal del Alto Orinoco")),
             dict(texto="El desnivel entre sus dos extremos: apenas veintiún metros.", stat=("21 m", "de desnivel entre extremos")),
         ]),
    # 5 · Triple Frontera
    dict(titulo="4 · La Triple Frontera", sub="Argentina · Brasil · Paraguay",
         colores={"ARG": TURQUESA, "BRA": VERDE, "PRY": ROJO},
         nombres={"ARG": (-54.75, -25.75), "BRA": (-54.40, -25.42), "PRY": (-54.80, -25.45)},
         rios=[("iguazu", 1, 3.0), ("parana", 1, 4.0)],
         marcas=[(*CIUDAD_DEL_ESTE, "Ciudad del Este", "izq", 1), (*FOZ, "Foz do Iguaçu", "der", 1),
                 (*PTO_IGUAZU, "Puerto Iguazú", "der", 1), (*CATARATAS, "Cataratas", "abajo", 3)],
         pulsos=[(*TRI_ARG_BRA_PRY, 1)],
         frases=[
             dict(texto="Bajamos al sur, a la Triple Frontera.", cam=(-55.0, -24.5, 6.0)),
             dict(texto="Aquí el río Iguazú se une al Paraná, y se tocan Argentina, Brasil y Paraguay.",
                  cam=(-54.58, -25.55, 0.75)),
             dict(texto="Cada país levantó un obelisco con sus colores, y desde cada uno se ven los otros dos países.",
                  cam=(-54.59, -25.58, 0.38)),
             dict(texto="Las Cataratas del Iguazú están en la frontera entre Argentina y Brasil.", cam=(-54.5, -25.63, 0.55)),
             dict(texto="Paraguay no tiene acceso a ellas."),
         ]),
    # 6 · Itaipú
    dict(titulo="5 · Itaipú", sub="Una presa, dos países",
         colores={"BRA": VERDE, "PRY": ROJO},
         nombres={"BRA": (-54.2, -24.6), "PRY": (-55.1, -24.9)},
         marcas=[(*ITAIPU, "Itaipú", "der", 0)],
         flechas=[dict(pts=[ITAIPU, (-52.2, -24.2), (-49.5, -23.6)], from_idx=5, dur=3.0, texto="a Brasil")],
         frases=[
             dict(texto="Unos kilómetros río arriba, el Paraná sostiene a Itaipú.", cam=(-54.56, -25.2, 0.9)),
             dict(texto="Es mitad de Brasil y mitad de Paraguay.", cam=(-54.56, -25.35, 0.5)),
             dict(texto="Tiene veinte turbinas: diez generan a cincuenta hertz, para Paraguay… y diez a sesenta, para Brasil.",
                  stat=("50 Hz + 60 Hz", "diez turbinas para cada país")),
             dict(texto="Paraguay obtiene de Itaipú cerca del ochenta y siete por ciento de su electricidad,",
                  cam=(-57.5, -23.8, 9.0), stat=("≈ 87 %", "de la electricidad de Paraguay")),
             dict(texto="según cifras de dos mil veinticinco."),
             dict(texto="Y vende gran parte de lo que le sobra a Brasil.", cam=(-53.5, -24.0, 11.0)),
         ]),
    # 7 · Río de la Plata
    dict(titulo="6 · El Río de la Plata", sub="Argentina · Uruguay",
         colores={"ARG": TURQUESA, "URY": ROSA}, nombres={"ARG": (-60.5, -34.5), "URY": (-55.9, -32.9)},
         rios=[("uruguay", 0, 4.0)],
         medidas=[dict(pts=[PUNTA_RASA, PUNTA_DEL_ESTE], texto="≈ 220 km", from_idx=1)],
         frases=[
             dict(texto="Más al sur, el Paraná y el Uruguay se juntan y forman el Río de la Plata.", cam=(-57.5, -33.0, 9.0)),
             dict(texto="Es la frontera entre Argentina y Uruguay, y mide hasta unos doscientos veinte kilómetros de ancho.",
                  cam=(-55.8, -35.4, 5.0), stat=("≈ 220 km", "de ancho en su desembocadura")),
             dict(texto="Por eso muchos lo llaman el río más ancho del mundo."),
             dict(texto="Otros dicen que no es un río, sino un estuario, o un golfo del Atlántico. Tú decides.",
                  cam=(-57.0, -34.8, 7.0)),
         ]),
    # 8 · Silala
    dict(titulo="7 · El Silala", sub="Bolivia · Chile",
         colores={"BOL": AMBAR, "CHL": ROJO}, nombres={"BOL": (-67.2, -21.2), "CHL": (-69.6, -23.1)},
         marcas=[(*SILALA, "Silala", "arriba", 0)], pulsos=[(*SILALA, 0)],
         frases=[
             dict(texto="En la frontera entre Bolivia y Chile hay un río con una gran historia: el Silala.", cam=(-68.03, -22.03, 3.0)),
             dict(texto="Durante años, los dos países discutieron sobre su naturaleza y su uso.", cam=(-68.03, -22.03, 1.4)),
             dict(texto="En diciembre de dos mil veintidós, la Corte Internacional de Justicia dictaminó que es un río internacional,",
                  cam=(-67.9, -22.2, 4.0), stat=("1 dic 2022", "Corte Internacional de Justicia")),
             dict(texto="y que Chile tiene derecho a un uso equitativo y razonable."),
             dict(texto="Bolivia conserva la soberanía sobre el manantial.", cam=(-68.03, -22.03, 0.9)),
         ]),
    # 9 · Oiapoque
    dict(titulo="8 · El Oiapoque", sub="Brasil · Guayana Francesa",
         colores={"BRA": VERDE, "GUF": VIOLETA}, nombres={"BRA": (-52.4, 1.9), "GUF": (-53.0, 3.9)},
         marcas=[(*OIAPOQUE, "Oiapoque", "abajo", 0), (*SAINT_GEORGES, "Saint-Georges", "arriba", 0),
                 (*CAYENA, "Cayena", "der", 4), (*MACAPA, "Macapá", "der", 4)],
         flechas=[dict(pts=[CAYENA, SAINT_GEORGES, OIAPOQUE, (-51.0, 2.05), (-50.8, 1.0), MACAPA],
                       from_idx=4, dur=4.0, dash=True)],
         frases=[
             dict(texto="Subimos al extremo norte: el río Oiapoque separa Brasil de la Guayana Francesa,", cam=(-52.0, 3.9, 3.0)),
             dict(texto="territorio de Francia en Sudamérica."),
             dict(texto="En dos mil diecisiete se inauguró un puente de trescientos setenta y ocho metros.",
                  cam=(-51.82, 3.87, 0.5), stat=("378 m", "puente inaugurado en 2017")),
             dict(texto="Fue la primera conexión terrestre internacional de la Guayana Francesa.", cam=(-51.82, 3.87, 0.3)),
             dict(texto="Desde dos mil veinte se puede ir en coche desde Cayena hasta Macapá.", cam=(-51.7, 2.5, 7.5)),
         ]),
    # 10 · Pilcomayo
    dict(titulo="9 · El Pilcomayo", sub="Argentina · Bolivia · Paraguay",
         colores={"ARG": TURQUESA, "BOL": AMBAR, "PRY": ROJO},
         nombres={"ARG": (-63.5, -25.8), "BOL": (-64.8, -19.6), "PRY": (-58.2, -22.0)},
         rios=[("pilcomayo", 0, 7.0)], wiggle=("pilcomayo", 2, None),
         frases=[
             dict(texto="Y llegamos al río que se mueve: el Pilcomayo.", cam=(-62.0, -22.3, 10.0)),
             dict(texto="Nace en Bolivia y, en gran parte de su curso bajo, es la frontera entre Argentina y Paraguay.",
                  cam=(-60.0, -23.6, 7.0)),
             dict(texto="Arrastra tantos sedimentos, y tiene tan poca pendiente, que se desborda y cambia de cauce.",
                  cam=(-59.5, -24.0, 4.5)),
             dict(texto="Por eso, en mil novecientos cinco, Argentina y Paraguay crearon una comisión mixta",
                  stat=("1905", "comisión mixta")),
             dict(texto="para decidir cuál era el cauce principal."),
             dict(texto="Y en mil novecientos cuarenta y cinco firmaron otro tratado, para fijar la frontera donde no hay un cauce fijo.",
                  stat=("1945", "nuevo tratado")),
         ]),
    # 11 · Dato final
    dict(titulo="Dato final", sub="Una frontera hecha de ríos",
         colores={"ARG": TURQUESA, "PRY": ROJO, "BOL": AMBAR}, nombres={"ARG": (-63.0, -28.0), "PRY": (-58.4, -23.0)},
         rios=[("paraguay", 1, 3.0)],
         marcas=[(*HITO_ESMERALDA, "Hito Esmeralda", "der", 2)], pulsos=[(*HITO_ESMERALDA, 2)],
         frases=[
             dict(texto="Un último dato: la frontera entre Argentina y Paraguay mide mil seiscientos ochenta y nueve kilómetros.",
                  cam=(-59.0, -25.0, 16.0), stat=("1.689 km", "frontera Argentina–Paraguay")),
             dict(texto="Y está definida únicamente por tres ríos: el Pilcomayo, el Paraná y el Paraguay."),
             dict(texto="El punto donde se juntan Argentina, Bolivia y Paraguay se llama Hito Esmeralda, a orillas del Pilcomayo…",
                  cam=(-62.65, -22.23, 1.8)),
             dict(texto="aunque una fuente dice que hoy podría estar seco por los sedimentos."),
         ]),
    # 12 · Cierre
    dict(titulo="Sudamérica", sub="Ríos que unen y separan", todos_los_rios=True,
         colores={"PER": AMBAR, "COL": ROJO, "BRA": VERDE, "ECU": VIOLETA, "VEN": VIOLETA, "ARG": TURQUESA,
                  "PRY": ROJO, "BOL": AMBAR, "CHL": ROSA, "URY": ROSA, "GUF": VIOLETA}, nombres={},
         frases=[
             dict(texto="Nueve historias, un mismo patrón: en Sudamérica, los ríos no solo separan países.", cam=SA),
             dict(texto="También los obligan a ponerse de acuerdo.", cam=(-60.0, -18.0, 38.0)),
             dict(texto="¿Cuál te sorprendió más? Cuéntamelo en los comentarios y sígueme para el próximo mapa.",
                  cam=(-60.0, -16.0, 52.0)),
         ]),
]
