"""Escenas de «¿Sabías que…? Los mapas te mienten: 8 curiosidades sobre los propios mapas».

Escena: titulo, sub, colores {ISO3 | "@Continente": color}, etiquetas [(lon, lat, texto)], frases y, opcionales:
  morph=(frase, m, dur)   proyección: m=0 Mercator, m=1 Equal Earth (el mapa se transforma en directo)
  graticula / tissot      malla de meridianos y paralelos / círculos iguales para ver la deformación
  arrastre                arrastra un país por la esfera (tamaño real) hasta otro lugar
  rutas                   líneas sobre el mapa (rumbo constante frente a círculo máximo)
  marcas [(lon, lat, texto, dirección, desde_frase)], pulsos [(lon, lat, desde_frase)]
  bir_tawil, estados, kong, california, america   capas especiales de cada curiosidad
Cada frase: texto (se narra y sale como subtítulo), cam=(lon, lat, ancho en grados) y stat=(cifra, etiqueta).
"""
AMBAR, ROJO, VERDE, VIOLETA, TURQUESA, ROSA = "#F4B942", "#E4572E", "#7FB069", "#9D8DF1", "#4ECDC4", "#FF8FA3"

MUNDO = (0.0, 12.0, 330.0)

LONDRES, NUEVA_YORK = (-0.13, 51.51), (-74.0, 40.71)
NULL = (0.0, 0.0)
AGLOE = (-74.92, 41.99)      # aproximado: al norte de Roscoe, en el cruce de la NY 206 con Morton Hill Road
KONG = (-4.61, 9.15)         # ciudad de Kong (Costa de Marfil)

SCENES = [
    # 0 · Gancho
    dict(titulo="¿SABÍAS QUE…?", sub="Los mapas te mienten", titulo_size=92,
         colores={"GRL": ROJO, "@Africa": TURQUESA}, graticula=True, tissot=True,
         arrastre=dict(iso="GRL", destino="@Africa", desde=3, dur=7.0, texto="Groenlandia"),
         frases=[
             dict(texto="¿Sabías que el mapa del mundo que has visto toda tu vida te está mintiendo?", cam=MUNDO),
             dict(texto="Mira Groenlandia: parece tan grande como África.", cam=(0.0, 22.0, 150.0)),
             dict(texto="Pero no lo es."),
             dict(texto="Fíjate lo que pasa si llevamos Groenlandia hasta el ecuador.", cam=(-5.0, 28.0, 120.0)),
             dict(texto="Se encoge. África es unas catorce veces más grande.", cam=(8.0, 14.0, 110.0),
                  stat=("≈ 14 ×", "África frente a Groenlandia")),
             dict(texto="Hoy: ocho curiosidades sobre los propios mapas.", cam=MUNDO, stat=("8", "curiosidades")),
         ]),
    # 1 · Mercator
    dict(titulo="1 · La proyección Mercator", sub="Un mapa hecho para navegar",
         colores={}, graticula=True, tissot=True,
         marcas=[(*LONDRES, "Londres", "arriba", 1), (*NUEVA_YORK, "Nueva York", "abajo", 1)],
         rutas=[dict(tipo="rumbo", a=LONDRES, b=NUEVA_YORK, desde=1, dur=3.5, texto="rumbo constante"),
                dict(tipo="circulo", a=LONDRES, b=NUEVA_YORK, desde=3, dur=3.5, texto="la más corta")],
         frases=[
             dict(texto="En mil quinientos sesenta y nueve, Gerardus Mercator publicó un mapa pensado para los navegantes.",
                  cam=(-35.0, 38.0, 130.0), stat=("1569", "Gerardus Mercator")),
             dict(texto="En su proyección, una línea recta es un rumbo constante de brújula.", cam=(-40.0, 47.0, 72.0)),
             dict(texto="Trazas la línea, mantienes el rumbo… y llegas."),
             dict(texto="Pero no es la ruta más corta: la más corta es esa curva, el círculo máximo."),
             dict(texto="El precio: cuanto más te alejas del ecuador, más infla los tamaños.", cam=MUNDO),
         ]),
    # 2 · Imposible
    dict(titulo="2 · El mapa perfecto no existe", sub="Aplanar una esfera siempre deforma",
         colores={"GRL": ROJO, "@Africa": TURQUESA}, graticula=True, tissot=True, morph=(0, 1.0, 5.0),
         frases=[
             dict(texto="Y no es un fallo de Mercator: aplanar una esfera sin deformarla es imposible.", cam=MUNDO),
             dict(texto="Cada mapa elige qué sacrificar: tamaños, formas, ángulos o distancias."),
             dict(texto="En dos mil dieciocho, tres cartógrafos, Šavrič, Jenny y Patterson, presentaron la proyección Equal Earth.",
                  stat=("2018", "Equal Earth")),
             dict(texto="Mantiene el tamaño relativo de las áreas: aquí Groenlandia es solo el siete por ciento de África.",
                  cam=(0.0, 12.0, 170.0), stat=("≈ 7 %", "Groenlandia frente a África")),
             dict(texto="El proyecto nació después de que las escuelas públicas de Boston, en dos mil diecisiete, adoptaran otra proyección.",
                  cam=MUNDO),
         ]),
    # 3 · América
    dict(titulo="3 · Cómo se bautizó América", sub="El mapa de Waldseemüller, 1507",
         colores={}, graticula=False, morph=(0, 0.0, 2.0), america=True,
         frases=[
             dict(texto="En mil quinientos siete, el cartógrafo Martin Waldseemüller imprimió el primer mapa donde aparece el nombre América.",
                  cam=(-52.0, -8.0, 80.0), stat=("1507", "primer mapa con «América»")),
             dict(texto="La llamó así por Américo Vespucio, creyendo, por error, que él y no Colón había descubierto aquellas tierras."),
             dict(texto="Solo se conserva un ejemplar."),
             dict(texto="La Biblioteca del Congreso de Estados Unidos lo compró por diez millones de dólares, y completó la compra en dos mil tres.",
                  stat=("10 M $", "pagados por el único ejemplar")),
         ]),
    # 4 · Isla Nula
    dict(titulo="4 · La Isla Nula", sub="Una isla que no existe",
         colores={}, graticula=True,
         marcas=[(*NULL, "0° N, 0° E", "arriba", 1)], pulsos=[(*NULL, 1)],
         frases=[
             dict(texto="Y existe una isla que no existe: la Isla Nula.", cam=(0.0, 0.0, 40.0)),
             dict(texto="Está en las coordenadas cero, cero: donde el ecuador cruza el meridiano de Greenwich, en el golfo de Guinea.",
                  cam=(0.0, 0.0, 9.0)),
             dict(texto="No hay tierra: solo mar y una boya meteorológica llamada Soul, como la música."),
             dict(texto="Pero casi todos los sistemas de mapas la conocen, porque cuando falla la geolocalización de algo, a veces lo colocan allí por defecto.",
                  cam=(0.0, 0.0, 4.0)),
             dict(texto="Incluso Natural Earth, la base de datos de este vídeo, puso allí una isla ficticia de un metro cuadrado, según una de las fuentes.",
                  cam=(0.0, 0.0, 2.0), stat=("1 m²", "isla ficticia en el 0,0")),
         ]),
    # 5 · Bir Tawil
    dict(titulo="5 · Bir Tawil", sub="La tierra que nadie reclama",
         colores={"EGY": "#CFC7B4", "SDN": "#CFC7B4"}, graticula=False, bir_tawil=True,
         etiquetas=[(34.4, 23.7, "EGIPTO"), (34.4, 20.3, "SUDÁN")],
         frases=[
             dict(texto="Hay un trozo de tierra que ningún país quiere: Bir Tawil, entre Egipto y Sudán.", cam=(33.7, 21.8, 3.2)),
             dict(texto="Todo por dos fronteras: en mil ochocientos noventa y nueve, una línea recta; en mil novecientos dos, otra, que seguía el uso de las tribus.",
                  cam=(34.3, 21.9, 5.0)),
             dict(texto="Egipto defiende la primera y Sudán la segunda."),
             dict(texto="Así, el triángulo de Hala'ib lo reclaman los dos… y Bir Tawil, ninguno.", cam=(35.0, 21.9, 6.8),
                  stat=("0 países", "reclaman Bir Tawil")),
             dict(texto="Reclamar Bir Tawil debilitaría su argumento sobre Hala'ib, que es mayor y tiene costa en el mar Rojo."),
         ]),
    # 6 · Agloe
    dict(titulo="6 · Agloe", sub="El pueblo que solo existía en el mapa",
         colores={"USA": "#8E8672", "CAN": "#8E8672"}, graticula=False, estados={"New York": "#EADFB6"},
         marcas=[(*AGLOE, "Agloe", "arriba", 1), (*AGLOE, "tienda (años 50)", "abajo", 4)], pulsos=[(*AGLOE, 4)],
         frases=[
             dict(texto="Los cartógrafos también ponían trampas.", cam=(-75.5, 42.6, 6.0)),
             dict(texto="Hace casi un siglo, la General Drafting Company inventó un pueblo en el estado de Nueva York: Agloe.",
                  cam=(-75.0, 42.2, 2.6)),
             dict(texto="Su nombre es un anagrama de las iniciales de sus autores, Otto Lindberg y Ernest Alpers."),
             dict(texto="Si aparecía en el mapa de un rival, era la prueba de que lo habían copiado."),
             dict(texto="Y entonces ocurrió algo increíble: en los años cincuenta, alguien construyó una tienda justo en ese cruce.",
                  cam=(-74.92, 41.99, 0.5)),
             dict(texto="Un pueblo inventado acabó existiendo de verdad."),
         ]),
    # 7 · Montes Kong
    dict(titulo="7 · Los Montes Kong", sub="La cordillera que nunca existió",
         colores={}, graticula=False, kong=True,
         marcas=[(*KONG, "Kong", "abajo", 3)],
         frases=[
             dict(texto="A veces, el error duró un siglo. Los Montes Kong: una cordillera enorme en África Occidental… que no existe.",
                  cam=(-3.0, 9.5, 26.0)),
             dict(texto="Aparece en el mapa de James Rennell de mil setecientos noventa y ocho, para apoyar su teoría sobre el curso del río Níger.",
                  cam=(-3.0, 9.8, 20.0)),
             dict(texto="Según un estudio, cuarenta mapas la dibujaron entre mil setecientos noventa y ocho y mil ochocientos noventa y dos.",
                  stat=("40 mapas", "con montañas inexistentes")),
             dict(texto="Hasta que un explorador francés, Louis Binger, llegó a la ciudad de Kong y encontró mezquitas, no montañas.",
                  cam=(-4.6, 9.2, 6.0)),
         ]),
    # 8 · California
    dict(titulo="8 · La isla de California", sub="Una isla en los mapas durante más de un siglo",
         colores={}, graticula=False, california=True,
         etiquetas=[(-119.5, 36.5, "ISLA DE\nCALIFORNIA")],
         frases=[
             dict(texto="Y California fue una isla en los mapas durante más de un siglo.", cam=(-118.0, 35.5, 20.0)),
             dict(texto="La idea viene de una novela de mil quinientos diez, Las sergas de Esplandián, y se afianzó con mapas hechos hacia mil seiscientos veinte."),
             dict(texto="El jesuita Eusebio Kino viajó por tierra entre mil seiscientos noventa y ocho y mil setecientos uno, y concluyó que estaba unida al continente.",
                  cam=(-114.0, 31.5, 12.0)),
             dict(texto="Aun así, los mapas siguieron mostrándola como isla; una fuente señala que el costo de las planchas de impresión ayudó a que el error durara.",
                  cam=(-118.0, 35.5, 20.0)),
             dict(texto="En mil setecientos cuarenta y siete, un decreto del rey Fernando Sexto declaró que California no era una isla.",
                  stat=("1747", "decreto de Fernando VI")),
         ]),
    # 9 · Cierre
    dict(titulo="Los mapas no son la realidad", sub="Son decisiones", colores={"GRL": ROJO, "@Africa": TURQUESA},
         graticula=True, tissot=True, morph=(0, 0.0, 1.5),
         frases=[
             dict(texto="Los mapas no son la realidad: son decisiones.", cam=MUNDO),
             dict(texto="Decisiones sobre tamaños, nombres, fronteras… y hasta trampas."),
             dict(texto="La próxima vez que veas un mapa, pregúntate: ¿qué me está ocultando?"),
             dict(texto="Cuéntame cuál te sorprendió más, y sígueme para el próximo mapa.", cam=(0.0, 12.0, 340.0)),
         ]),
]
