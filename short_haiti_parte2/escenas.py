"""Escenas de «Haití y República Dominicana · Parte 2: la ocupación (1801-1856)».

Cada escena: narración (texto para la voz), título, subtítulo, color del oeste y del este,
cámara (lon, lat, ancho en grados), marcadores [(lon, lat, texto)] y flecha opcional ((lon, lat) -> (lon, lat)).
La duración de cada escena la marca su narración (ver narrar_parte2.py).
"""
ESP, FRA, HTI, DOM, HESP, NEUTRO = "#FFC400", "#8E7CC3", "#D7263D", "#3A8DDE", "#7FD1B9", "#BDB5A6"

ISLA = (-71.4, 18.9, 6.9)
ESTE = (-70.3, 18.8, 3.6)
SUR = (-70.3, 18.75, 2.6)
NORTE = (-71.4, 19.35, 2.6)

PAP = (-72.34, 18.54)          # Puerto Príncipe
SDQ = (-69.93, 18.47)          # Santo Domingo
CAP = (-72.20, 19.76)          # Cabo Haitiano

SCENES = [
    dict(voz="¿Sabías que hubo un país llamado Haití Español… y que duró apenas unas semanas?",
         titulo="Parte 2", sub="La ocupación haitiana", oeste=HTI, este=DOM, cam=ISLA),
    dict(voz="Esta es la historia de cómo Haití llegó a gobernar toda la isla… y de cómo los dominicanos lo recuperaron todo.",
         titulo="1801 – 1856", sub="Medio siglo de lucha por el este", oeste=HTI, este=DOM, cam=ISLA),
    dict(voz="Mil ochocientos uno. Haití ni siquiera existe todavía. Pero Toussaint Louverture, que manda en la colonia francesa del oeste, cruza la isla… y toma Santo Domingo.",
         titulo="1801", sub="Toussaint Louverture toma Santo Domingo", oeste=FRA, este=ESP, cam=ISLA,
         marcas=[(*SDQ, "Santo Domingo")], flecha=(PAP, SDQ)),
    dict(voz="Dato curioso: luchaba contra la esclavitud… pero en el este no llegó a abolirla. Y en mil ochocientos dos, una expedición francesa le obliga a volver al oeste.",
         titulo="1802", sub="Toussaint se retira al oeste", oeste=FRA, este=ESP, cam=ISLA,
         marcas=[(*SDQ, "Santo Domingo")], flecha=(SDQ, PAP)),
    dict(voz="Mil ochocientos cinco. Haití ya es independiente. Dessalines sitia Santo Domingo… y fracasa.",
         titulo="1805", sub="Dessalines sitia Santo Domingo… y fracasa", oeste=HTI, este=FRA, cam=ISLA,
         marcas=[(*SDQ, "Santo Domingo")], flecha=(PAP, SDQ)),
    dict(voz="Mil ochocientos veintiuno. José Núñez de Cáceres declara la independencia de España. Nace un país nuevo: el Estado Independiente del Haití Español.",
         titulo="1821", sub="Nace el «Haití Español»", oeste=HTI, este=HESP, cam=ESTE,
         marcas=[(*SDQ, "Santo Domingo")]),
    dict(voz="Pero los pueblos de la frontera, como Montecristi y Dajabón, no lo siguen. Piden unirse… ¡a Haití!",
         titulo="La frontera se divide", sub="Montecristi y Dajabón piden unirse a Haití", oeste=HTI, este=HESP, cam=NORTE,
         marcas=[(-71.65, 19.85, "Montecristi"), (-71.71, 19.55, "Dajabón")]),
    dict(voz="Nueve de febrero de mil ochocientos veintidós. El presidente haitiano Jean-Pierre Boyer entra en Santo Domingo con unos diez mil soldados. El Haití Español desaparece.",
         titulo="9 de febrero de 1822", sub="Boyer entra en Santo Domingo\ncon unos 10.000 soldados", oeste=HTI, este=HTI, cam=ISLA,
         marcas=[(*SDQ, "Santo Domingo")], flecha=(PAP, SDQ)),
    dict(voz="Toda la isla pasa a ser Haití. Y lo primero que hace Boyer… es abolir la esclavitud en el este, y prometer tierras a los libertos.",
         titulo="Una sola isla, un solo país", sub="Boyer abolió la esclavitud en el este", oeste=HTI, este=HTI, cam=ISLA),
    dict(voz="Pero también cierra la Universidad Santo Tomás de Aquino, considerada la más antigua de América… y manda a sus estudiantes al ejército.",
         titulo="Universidad cerrada", sub="Los estudiantes, al ejército", oeste=HTI, este=HTI, cam=SUR,
         marcas=[(*SDQ, "Santo Domingo")]),
    dict(voz="Con el Código Rural, Boyer quiere obligar a los campesinos a cultivar para exportar. Muchos se resisten… y las exportaciones se hunden.",
         titulo="El Código Rural", sub="Cultivar para exportar… a la fuerza", oeste=HTI, este=HTI, cam=ISLA),
    dict(voz="Y en mil ochocientos veinticinco, Francia exige un pago a cambio de reconocer a Haití: ciento cincuenta millones de francos. Una deuda que tardaría más de medio siglo en saldarse.",
         titulo="1825", sub="150 millones de francos para Francia", oeste=HTI, este=HTI, cam=ISLA),
    dict(voz="Dieciséis de julio de mil ochocientos treinta y ocho. Juan Pablo Duarte funda en secreto La Trinitaria. Su objetivo: la independencia.",
         titulo="1838 · La Trinitaria", sub="Juan Pablo Duarte se organiza en secreto", oeste=HTI, este=HTI, cam=SUR,
         marcas=[(*SDQ, "Santo Domingo")]),
    dict(voz="Mil ochocientos cuarenta y tres. Estalla en Haití una revolución contra Boyer. ¿Y qué hacen los trinitarios? ¡Se alían con los rebeldes haitianos!",
         titulo="1843 · La Reforma", sub="Trinitarios y rebeldes haitianos,\njuntos contra Boyer", oeste=HTI, este=HTI, cam=ISLA,
         marcas=[(*PAP, "Puerto Príncipe")]),
    dict(voz="Boyer cae. Pero Duarte acaba en el exilio… y se pierde el gran día.",
         titulo="Boyer cae", sub="Duarte, al exilio", oeste=HTI, este=HTI, cam=ISLA),
    dict(voz="Veintisiete de febrero de mil ochocientos cuarenta y cuatro. ¡Se proclama la República Dominicana!",
         titulo="27 de febrero de 1844", sub="¡Independencia!", oeste=HTI, este=DOM, cam=ISLA,
         marcas=[(*SDQ, "Santo Domingo")]),
    dict(voz="Pero Haití no se rinde. Diecinueve de marzo: batalla de Azua. Treinta de marzo: batalla de Santiago. Haití no consigue recuperar el este.",
         titulo="1844", sub="Batallas de Azua y Santiago", oeste=HTI, este=DOM, cam=ESTE,
         marcas=[(-70.73, 18.45, "Azua"), (-70.70, 19.45, "Santiago")]),
    dict(voz="Mil ochocientos cuarenta y nueve: El Número y Las Carreras. Mil ochocientos cincuenta y cinco: Santomé y Cambronal. Mil ochocientos cincuenta y seis: Sabana Larga.",
         titulo="1849 – 1856", sub="Más invasiones, más batallas", oeste=HTI, este=DOM, cam=ESTE,
         marcas=[(-70.55, 18.38, "El Número"), (-70.40, 18.30, "Las Carreras", "abajo"), (-71.23, 18.80, "Santomé"),
                 (-71.40, 18.50, "Cambronal", "abajo"), (-71.45, 19.62, "Sabana Larga")]),
    dict(voz="Doce años de guerra después de la independencia… y Haití nunca recuperó el este.",
         titulo="12 años de guerra", sub="Y la independencia se mantiene", oeste=HTI, este=DOM, cam=ISLA),
    dict(voz="Una isla. Dos países. Y una historia mucho más complicada… de lo que te contaron.",
         titulo="Una isla, dos países", sub="Sígueme para la parte 3", oeste=HTI, este=DOM, cam=(-71.7, 19.0, 3.0),
         etiquetas=[(-72.45, 19.25), (-70.95, 18.8)]),
]
