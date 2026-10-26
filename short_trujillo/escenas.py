"""Escenas de «Trujillo contra Venezuela: el atentado que aisló a un dictador».

Cada escena: narración (voz), título, subtítulo, colores {código ISO3: color}, cámara (lon, lat, ancho en grados),
etiquetas de países [(lon, lat, texto)], marcadores [(lon, lat, texto[, "abajo"])] y flecha opcional.
La duración de cada escena la marca su narración (ver narrar.py).
"""
RD, VEN, CUB, CRI, USA = "#B3123B", "#FFC400", "#7FD1B9", "#8E7CC3", "#3A8DDE"

CARIBE = (-74.0, 14.0, 27.0)
ISLA = (-70.4, 18.9, 4.6)
VENEZ = (-66.5, 9.0, 14.0)
CUBA_RD = (-75.4, 20.3, 15.4)
CARACAS = (-66.9, 10.2, 6.0)
COSTA_RICA = (-76.6, 13.0, 20.4)

SDQ = (-69.93, 18.47)
CCS = (-66.90, 10.49)
HAV = (-82.37, 23.13)
SJO = (-84.09, 9.93)
WAS = (-77.04, 38.90)

E_RD = [(-70.5, 19.15, "REPÚBLICA\nDOMINICANA")]
E_VEN = [(-66.0, 7.2, "VENEZUELA")]

SCENES = [
    dict(voz="Un dictador del Caribe intentó matar al presidente de otro país… y casi lo consigue.",
         titulo="Trujillo contra Venezuela", sub="El atentado que aisló a un dictador",
         colores={"DOM": RD, "VEN": VEN}, cam=CARIBE, etiquetas=E_VEN,
         marcas=[(*SDQ, "Ciudad Trujillo"), (*CCS, "Caracas", "abajo")], flecha=(SDQ, CCS)),
    dict(voz="Rafael Leónidas Trujillo gobernó la República Dominicana con mano de hierro durante treinta y un años: de mil novecientos treinta a mil novecientos sesenta y uno.",
         titulo="1930 – 1961", sub="31 años de dictadura", colores={"DOM": RD}, cam=ISLA, etiquetas=E_RD),
    dict(voz="Su culto llegó tan lejos que, en mil novecientos treinta y seis, le cambió el nombre a la capital. Santo Domingo pasó a llamarse… Ciudad Trujillo.",
         titulo="1936", sub="Santo Domingo pasa a llamarse\n«Ciudad Trujillo»", colores={"DOM": RD}, cam=ISLA,
         etiquetas=E_RD, marcas=[(*SDQ, "Ciudad Trujillo")]),
    dict(voz="Pero sus enemigos se organizaban fuera del país. Y uno de los más duros estaba en Venezuela: el presidente Rómulo Betancourt.",
         titulo="Rómulo Betancourt", sub="Presidente de Venezuela\ny enemigo de Trujillo", colores={"DOM": RD, "VEN": VEN},
         cam=VENEZ, etiquetas=E_VEN, marcas=[(*CCS, "Caracas")]),
    dict(voz="Catorce de junio de mil novecientos cincuenta y nueve. Exiliados dominicanos despegan desde Cuba y aterrizan en Constanza. Días después, otros desembarcan en Maimón y Estero Hondo.",
         titulo="14 de junio de 1959", sub="Invasión desde Cuba", colores={"DOM": RD, "CUB": CUB}, cam=CUBA_RD,
         marcas=[(-70.75, 18.91, "Constanza", "abajo"), (-71.0, 19.85, "Maimón y\nEstero Hondo")],
         flecha=(HAV, (-70.75, 18.91))),
    dict(voz="La invasión fracasa. Pero aquellos hombres se convierten en un símbolo de la resistencia contra Trujillo.",
         titulo="Fracasan…", sub="…pero se convierten en símbolo", colores={"DOM": RD}, cam=ISLA, etiquetas=E_RD),
    dict(voz="Trujillo apunta a Venezuela. Y decide eliminar a Betancourt.",
         titulo="Objetivo: Betancourt", sub="", colores={"DOM": RD, "VEN": VEN}, cam=CARIBE, etiquetas=E_VEN,
         marcas=[(*SDQ, "Ciudad Trujillo"), (*CCS, "Caracas", "abajo")], flecha=(SDQ, CCS)),
    dict(voz="Veinticuatro de junio de mil novecientos sesenta. Caracas, avenida Los Próceres. Un coche bomba estalla al paso de la comitiva presidencial.",
         titulo="24 de junio de 1960", sub="Coche bomba en Caracas", colores={"VEN": VEN}, cam=CARACAS,
         marcas=[(*CCS, "Avenida Los Próceres")]),
    dict(voz="Mueren el jefe de la Casa Militar y un asistente. Betancourt sobrevive… pero queda gravemente herido.",
         titulo="Betancourt sobrevive", sub="Gravemente herido", colores={"VEN": VEN}, cam=CARACAS,
         marcas=[(*CCS, "Caracas")]),
    dict(voz="Al día siguiente, Betancourt acusa directamente a Trujillo. Y lleva el caso a la Organización de Estados Americanos.",
         titulo="Betancourt acusa a Trujillo", sub="El caso llega a la OEA", colores={"DOM": RD, "VEN": VEN}, cam=VENEZ,
         etiquetas=E_VEN, marcas=[(*CCS, "Caracas")]),
    dict(voz="Agosto de mil novecientos sesenta. San José, Costa Rica. Y por primera vez en su historia… la OEA sanciona a uno de sus miembros.",
         titulo="Agosto de 1960", sub="La OEA sanciona por primera vez\na un país miembro", colores={"DOM": RD, "CRI": CRI},
         cam=COSTA_RICA, marcas=[(*SDQ, "Ciudad Trujillo"), (*SJO, "San José", "abajo")], flecha=(SJO, SDQ)),
    dict(voz="Ruptura de relaciones y embargo de armas. Estados Unidos rompe relaciones el veintiséis de agosto… y suspende la cuota de azúcar dominicana.",
         titulo="Aislado", sub="Ruptura de relaciones y embargo de armas", colores={"DOM": RD, "USA": USA},
         cam=(-75.0, 26.0, 30.0), marcas=[(*SDQ, "Ciudad Trujillo", "abajo"), (*WAS, "Washington")], flecha=(WAS, SDQ)),
    dict(voz="Trujillo se queda solo. Y dentro del país, la represión se endurece.",
         titulo="Solo", sub="Y la represión se endurece", colores={"DOM": RD}, cam=ISLA, etiquetas=E_RD),
    dict(voz="Veinticinco de noviembre de mil novecientos sesenta. Asesinan a las hermanas Mirabal, opositoras al régimen. Hoy, ese día es el Día Internacional de la Eliminación de la Violencia contra la Mujer.",
         titulo="25 de noviembre de 1960", sub="Asesinan a las hermanas Mirabal", colores={"DOM": RD}, cam=ISLA, etiquetas=E_RD),
    dict(voz="Seis meses después, el treinta de mayo de mil novecientos sesenta y uno, Trujillo muere en una emboscada en la carretera. Entre los atacantes, había militares de su propio régimen.",
         titulo="30 de mayo de 1961", sub="Trujillo muere en una emboscada", colores={"DOM": RD}, cam=ISLA, etiquetas=E_RD,
         marcas=[(*SDQ, "Ciudad Trujillo")]),
    dict(voz="En enero de mil novecientos sesenta y dos, la OEA levanta las sanciones. Y la capital vuelve a llamarse… Santo Domingo.",
         titulo="1962", sub="Fin de las sanciones", colores={"DOM": USA}, cam=ISLA, etiquetas=E_RD,
         marcas=[(*SDQ, "Santo Domingo")]),
    dict(voz="Un dictador que quiso matar a un presidente extranjero… y acabó aislado por todo un continente.",
         titulo="Aislado por un continente", sub="Sígueme para más historia con mapas", colores={"DOM": RD, "VEN": VEN},
         cam=CARIBE, etiquetas=E_VEN, marcas=[(*SDQ, "Santo Domingo"), (*CCS, "Caracas", "abajo")]),
]
