"""Escenas de «Las siete invasiones haitianas (1801-1856)».

Cada escena: voz (narración), titulo, sub, colores del oeste/este, cam (lon, lat, ancho en grados),
etiquetas de región [(lon, lat, texto)], marcas [(lon, lat, texto, dirección)] y rutas.
Una ruta: dict(pts=[(lon, lat), ...], color, dash=True si el trazado es aproximado/no confirmado,
texto=(nombre del jefe), delay, dur). La duración de cada escena la marca su narración.
"""
ESP, FRA, HTI, DOM, HESP = "#FFC400", "#8E7CC3", "#D7263D", "#3A8DDE", "#7FD1B9"
AVANCE, RETIRADA = "#FFFFFF", "#FF9F1C"

ISLA = (-70.9, 18.95, 6.8)
MEDIA = (-70.9, 19.0, 5.4)
SUR = (-70.95, 18.65, 3.9)
NORTE = (-71.1, 19.45, 3.9)

# Lugares (lon, lat), aproximados
CAP = (-72.20, 19.76)    # Cabo Haitiano
PAP = (-72.34, 18.54)    # Puerto Príncipe
DAJ = (-71.71, 19.55)    # Dajabón
STG = (-70.69, 19.45)    # Santiago
MOCA = (-70.52, 19.39)
VEGA = (-70.53, 19.22)   # La Vega
SDQ = (-69.93, 18.47)    # Santo Domingo
BANI = (-70.33, 18.28)
AZUA = (-70.73, 18.45)
SJM = (-71.23, 18.81)    # San Juan de la Maguana
MATAS = (-71.52, 18.88)  # Las Matas de Farfán
NEIBA = (-71.42, 18.48)
CACHIMAN = (-71.68, 18.97)
ESTRELLETA = (-71.70, 18.86)
BELER = (-71.72, 19.62)
SABANA_LARGA = (-71.55, 19.50)
FUENTE_RODEO = (-70.66, 18.52)
EL_NUMERO = (-70.79, 18.40)
LAS_CARRERAS = (-70.40, 18.34)
OCOA = (-70.50, 18.52)
SANTOME = (-71.30, 18.84)
CAMBRONAL = (-71.44, 18.58)

# Puntos de entrada en la frontera (lado haitiano, aproximados)
F_NORTE = (-71.95, 19.62)
F_CENTRO = (-71.95, 18.92)
F_SUR = (-71.95, 18.50)

E_FRA_ESP = [(-72.6, 19.05, "SAINT-\nDOMINGUE"), (-70.0, 19.2, "ESPAÑA")]
E_HTI_FRA = [(-72.6, 19.05, "HAITÍ"), (-70.0, 19.2, "FRANCIA")]
E_HTI_HESP = [(-72.6, 19.05, "HAITÍ"), (-70.0, 19.2, "HAITÍ\nESPAÑOL")]
E_HTI = [(-71.0, 19.2, "HAITÍ")]
E_HTI_DOM = [(-72.6, 19.05, "HAITÍ"), (-70.0, 19.2, "REPÚBLICA\nDOMINICANA")]

SCENES = [
    dict(voz="Entre mil ochocientos uno y mil ochocientos cincuenta y seis, ejércitos haitianos entraron siete veces en el este de la isla. Vamos a recorrer cada invasión: sus jefes, sus rutas y sus resultados. Sin pasión: solo lo que dicen las fuentes.",
         titulo="Las siete invasiones", sub="Haití y el este de la isla, 1801–1856",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="Para entender el mapa: en mil ochocientos uno, el oeste era la colonia francesa de Saint-Domingue. El este seguía siendo español, aunque España se lo había cedido a Francia en mil setecientos noventa y cinco, por el Tratado de Basilea.",
         titulo="Antes de la primera invasión", sub="Oeste francés · este español (cedido a Francia en 1795)",
         oeste=FRA, este=ESP, cam=ISLA, etiquetas=E_FRA_ESP),
    dict(voz="Primera invasión. Enero de mil ochocientos uno. Toussaint Louverture, que gobernaba el oeste en nombre de Francia, envía a Moïse y a Paul Louverture con dos cuerpos de ejército. El pretexto: Francia no había tomado posesión del este. Las rutas exactas no están confirmadas; el dibujo es un esquema.",
         titulo="1801 · Primera invasión", sub="Toussaint Louverture, dos cuerpos de ejército",
         oeste=FRA, este=ESP, cam=ISLA, etiquetas=E_FRA_ESP, marcas=[(*SDQ, "Santo Domingo", "der")],
         rutas=[dict(pts=[CAP, DAJ, STG, VEGA, SDQ], dash=True, texto="Moïse", delay=1.2, dur=3.2),
                dict(pts=[PAP, NEIBA, AZUA, SDQ], dash=True, texto="Paul", delay=1.2, dur=3.2)]),
    dict(voz="El veintiséis o veintisiete de enero toma Santo Domingo, con poca resistencia. Las fuentes discrepan sobre si decretó entonces la abolición de la esclavitud en el este: Britannica dice que sí; otras dicen que no se aplicó. En mil ochocientos dos, una expedición francesa lo obliga a volver al oeste.",
         titulo="Enero de 1801", sub="Toma Santo Domingo… y en 1802 se retira",
         oeste=FRA, este=ESP, cam=ISLA, etiquetas=E_FRA_ESP, marcas=[(*SDQ, "Santo Domingo", "der")]),
    dict(voz="Segunda invasión. Haití ya es independiente, y el este está en manos francesas, bajo el general Ferrand. El seis de enero de mil ochocientos cinco, Ferrand proclama reabiertas las hostilidades. Dessalines y Christophe invaden con más de veinte mil hombres, según una fuente dominicana.",
         titulo="1805 · Segunda invasión", sub="Dessalines y Christophe",
         oeste=HTI, este=FRA, cam=ISLA, etiquetas=E_HTI_FRA, marcas=[(*SDQ, "Santo Domingo", "der")]),
    dict(voz="Christophe domina el Cibao: Santiago, Moca, La Vega. Dessalines sitia Santo Domingo desde el cinco de marzo. Llega una escuadra francesa, el sitio se levanta, y los haitianos se retiran.",
         titulo="Marzo de 1805", sub="Sitio de Santo Domingo",
         oeste=HTI, este=FRA, cam=ISLA, etiquetas=E_HTI_FRA, marcas=[(*SDQ, "Santo Domingo", "der")],
         rutas=[dict(pts=[CAP, DAJ, STG, MOCA, VEGA], dash=True, texto="Christophe", delay=1.2, dur=3.0),
                dict(pts=[PAP, AZUA, SDQ], dash=True, texto="Dessalines", delay=1.2, dur=3.0)]),
    dict(voz="En la retirada, las fuentes describen la destrucción de pueblos: Santiago, Moca, La Vega, Azua, San Juan y Baní. Se habla de unas diez mil muertes, y los historiadores dominicanos señalan Moca y Santiago como los peores casos. Son cifras de fuentes secundarias, con mucha variación.",
         titulo="La retirada de 1805", sub="Pueblos arrasados, según las fuentes",
         oeste=HTI, este=FRA, cam=MEDIA, etiquetas=[],
         marcas=[(*STG, "Santiago", "izq"), (*MOCA, "Moca", "arriba"), (*VEGA, "La Vega", "der"),
                 (*AZUA, "Azua", "abajo"), (*SJM, "San Juan", "arriba"), (*BANI, "Baní", "abajo")]),
    dict(voz="Tercera invasión. En diciembre de mil ochocientos veintiuno, José Núñez de Cáceres proclama el Estado Independiente del Haití Español. Pero algunos pueblos de la frontera piden unirse a Haití, y el presidente Jean-Pierre Boyer decide entrar.",
         titulo="1822 · Tercera invasión", sub="Boyer y el «Haití Español»",
         oeste=HTI, este=HESP, cam=ISLA, etiquetas=E_HTI_HESP, marcas=[(*SDQ, "Santo Domingo", "der")]),
    dict(voz="Del veinte de enero al nueve de febrero de mil ochocientos veintidós. Una columna, bajo Bonnet, entra por el noreste: Dajabón, Santiago, La Vega. Boyer sale el veintiocho de enero con unos doce mil hombres en dos columnas, pasa por Baní el seis de febrero, y entra en Santo Domingo el nueve, a las siete de la mañana, por la Puerta del Conde.",
         titulo="Enero – febrero de 1822", sub="Dos columnas hacia Santo Domingo",
         oeste=HTI, este=HESP, cam=ISLA, etiquetas=[],
         marcas=[(*DAJ, "Dajabón", "arriba"), (*STG, "Santiago", "arriba"), (*VEGA, "La Vega", "der"),
                 (*BANI, "Baní", "abajo"), (*SDQ, "Santo Domingo", "der")],
         rutas=[dict(pts=[F_NORTE, DAJ, STG, VEGA], texto="Bonnet", delay=1.2, dur=3.0),
                dict(pts=[PAP, NEIBA, AZUA, BANI], dash=True, texto="Boyer", delay=1.2, dur=3.0),
                dict(pts=[BANI, SDQ], texto=None, delay=4.4, dur=1.4)]),
    dict(voz="En las fuentes que encontré no aparece una batalla de importancia. Es la única invasión que deja la isla entera bajo un solo gobierno. Durará veintidós años.",
         titulo="9 de febrero de 1822", sub="Toda la isla, bajo Haití (22 años)",
         oeste=HTI, este=HTI, cam=ISLA, etiquetas=E_HTI, marcas=[(*SDQ, "Santo Domingo", "der")]),
    dict(voz="Veintisiete de febrero de mil ochocientos cuarenta y cuatro. Los dominicanos proclaman su independencia. Haití responde con la cuarta invasión: tres columnas, de veinte a treinta mil hombres, según las fuentes.",
         titulo="1844 · Cuarta invasión", sub="Haití responde a la independencia",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="Souffrand baja por Neiba. Hérard avanza por el valle de San Juan hacia Azua. Pierrot entra por Dajabón, rumbo a Santiago. Las fuentes no coinciden en quién llevaba cada columna del sur.",
         titulo="Marzo de 1844", sub="Tres columnas",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=[],
         marcas=[(*DAJ, "Dajabón", "arriba"), (*STG, "Santiago", "arriba"), (*AZUA, "Azua", "abajo")],
         rutas=[dict(pts=[F_NORTE, DAJ, STG], texto="Pierrot", delay=1.2, dur=3.0),
                dict(pts=[F_CENTRO, MATAS, SJM, AZUA], texto="Hérard", delay=1.2, dur=3.0),
                dict(pts=[F_SUR, NEIBA, AZUA], dash=True, texto="Souffrand", delay=1.2, dur=3.0)]),
    dict(voz="Trece de marzo: Fuente del Rodeo. Diecinueve de marzo: Azua. Unos dos mil doscientos dominicanos, con Santana y Duvergé, contra unos diez mil haitianos, según Wikipedia. Mil bajas haitianas contra dos dominicanas: cifras del bando vencedor, para tomar con cautela.",
         titulo="19 de marzo de 1844 · Azua", sub="Santana y Duvergé",
         oeste=HTI, este=DOM, cam=SUR, etiquetas=[],
         marcas=[(*FUENTE_RODEO, "Fuente del Rodeo", "arriba"), (*AZUA, "Azua", "abajo")]),
    dict(voz="Treinta de marzo: Santiago. Imbert, con unos tres mil hombres, contra diez mil de Pierrot. Pierrot se retira tras recibir un impreso falso que anunciaba la muerte de Hérard en Azua, y es perseguido hasta cerca de Dajabón.",
         titulo="30 de marzo de 1844 · Santiago", sub="Imbert contra Pierrot",
         oeste=HTI, este=DOM, cam=NORTE, etiquetas=[],
         marcas=[(*STG, "Santiago", "abajo"), (*DAJ, "Dajabón", "arriba")],
         rutas=[dict(pts=[STG, DAJ], color=RETIRADA, texto="Retirada", delay=1.4, dur=2.6)]),
    dict(voz="Quince de abril: Tortuguero. El tres de mayo, Hérard cae del poder en Haití. La invasión se detiene en menos de un mes, por dificultades de abastecimiento y por la resistencia dominicana.",
         titulo="Abril – mayo de 1844", sub="La invasión se detiene",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="Quinta invasión. En mil ochocientos cuarenta y cinco gobierna Pierrot. El veintidós de julio expulsa de Cachimán a una incursión dominicana, y el seis de agosto ordena invadir.",
         titulo="1845 · Quinta invasión", sub="Pierrot",
         oeste=HTI, este=DOM, cam=MEDIA, etiquetas=[],
         marcas=[(*CACHIMAN, "Cachimán", "arriba")],
         rutas=[dict(pts=[F_CENTRO, CACHIMAN, ESTRELLETA], texto="Pierrot", delay=1.2, dur=2.6)]),
    dict(voz="Diecisiete de septiembre: Estrelleta, en Elías Piña. Duvergé vence a un ejército haitiano mayor. Veintisiete de octubre: Beler, en Dajabón, junto a un fuerte llamado El Invencible. Los haitianos se retiran cruzando el río Dajabón.",
         titulo="Septiembre – octubre de 1845", sub="Estrelleta y Beler",
         oeste=HTI, este=DOM, cam=MEDIA, etiquetas=[],
         marcas=[(*ESTRELLETA, "Estrelleta", "der"), (*BELER, "Beler", "der")],
         rutas=[dict(pts=[BELER, F_NORTE], color=RETIRADA, texto="Retirada", delay=2.0, dur=2.0)]),
    dict(voz="Sexta invasión. Marzo de mil ochocientos cuarenta y nueve. Faustin Soulouque entra con unos dieciocho mil soldados por Las Matas de Farfán y San Juan hacia Azua, y llega hasta el río Ocoa, a unos ochenta y seis kilómetros de la capital.",
         titulo="1849 · Sexta invasión", sub="Soulouque llega hasta el río Ocoa",
         oeste=HTI, este=DOM, cam=SUR, etiquetas=[],
         marcas=[(*MATAS, "Las Matas", "arriba"), (*SJM, "San Juan", "arriba"), (*AZUA, "Azua", "abajo"),
                 (*OCOA, "Río Ocoa", "arriba")],
         rutas=[dict(pts=[F_CENTRO, MATAS, SJM, AZUA, OCOA], texto="Soulouque", delay=1.2, dur=3.6)]),
    dict(voz="Diecisiete de abril: Duvergé lo detiene en El Número, cerca de Azua. Hacia el veintiuno: Santana lo derrota en Las Carreras, cerca de Baní. Una fuente estima que Haití perdió más del doble de hombres que los dominicanos.",
         titulo="Abril de 1849", sub="El Número y Las Carreras",
         oeste=HTI, este=DOM, cam=SUR, etiquetas=[],
         marcas=[(*EL_NUMERO, "El Número", "izq"), (*LAS_CARRERAS, "Las Carreras", "abajo"),
                 (*AZUA, "Azua", "arriba"), (*BANI, "Baní", "arriba")],
         rutas=[dict(pts=[OCOA, AZUA, F_CENTRO], color=RETIRADA, texto=None, delay=1.8, dur=2.4)]),
    dict(voz="Séptima invasión. Noviembre de mil ochocientos cincuenta y cinco. Soulouque, ahora emperador con el nombre de Faustin Primero, divide su ejército en tres cuerpos: por Dajabón, por Las Matas de Farfán y por Neiba. Las fuentes hablan de entre doce mil y treinta mil hombres.",
         titulo="1855 · Séptima invasión", sub="Faustin I, tres cuerpos de ejército",
         oeste=HTI, este=DOM, cam=MEDIA, etiquetas=[],
         marcas=[(*DAJ, "Dajabón", "arriba"), (*MATAS, "Las Matas", "arriba"), (*NEIBA, "Neiba", "abajo")],
         rutas=[dict(pts=[F_NORTE, DAJ], texto="Norte", delay=1.2, dur=2.2),
                dict(pts=[F_CENTRO, MATAS], texto="Centro", delay=1.2, dur=2.2),
                dict(pts=[F_SUR, NEIBA], texto="Sur", delay=1.2, dur=2.2)]),
    dict(voz="Veintidós de diciembre: Santomé, cerca de Las Matas, ante Cabral; y Cambronal, cerca de Neiba, ante Sosa. En el norte, Sabana Larga, en Dajabón: unos ocho mil dominicanos, con Franco Bidó, contra unos veintidós mil haitianos. La fecha oscila entre diciembre de mil ochocientos cincuenta y cinco y el veinticuatro de enero de mil ochocientos cincuenta y seis.",
         titulo="1855 – 1856", sub="Santomé, Cambronal y Sabana Larga",
         oeste=HTI, este=DOM, cam=MEDIA, etiquetas=[],
         marcas=[(*SANTOME, "Santomé", "der"), (*CAMBRONAL, "Cambronal", "der"), (*SABANA_LARGA, "Sabana Larga", "der")]),
    dict(voz="Siete invasiones. Dos lograron tomar Santo Domingo: la de mil ochocientos uno y la de mil ochocientos veintidós. Cinco fracasaron: la de mil ochocientos cinco y las cuatro posteriores a la independencia dominicana.",
         titulo="El balance", sub="2 lograron tomar Santo Domingo · 5 fracasaron",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="¿Por qué ocurrieron? Los historiadores dominicanos hablan de una tesis de unificación: toda la isla bajo un solo Estado. Se mezclaron pretextos legales, la rivalidad con Francia, ambición de poder y llamamientos de pueblos fronterizos. Y fracasaron por abastecimiento, terreno y política interna de Haití.",
         titulo="¿Por qué?", sub="La tesis de la unificación",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="Una advertencia final: casi todas estas cifras vienen de fuentes dominicanas, del bando vencedor. Para un juicio completo, hay que contrastarlas con la historiografía haitiana.",
         titulo="Sobre las cifras", sub="Casi todas, de fuentes del bando vencedor",
         oeste=HTI, este=DOM, cam=ISLA, etiquetas=E_HTI_DOM),
    dict(voz="Siete invasiones. Doce años de guerra después de la independencia. Una isla, dos países… y una historia que todavía se discute.",
         titulo="Una isla, dos países", sub="Una historia que todavía se discute",
         oeste=HTI, este=DOM, cam=(-71.7, 19.0, 3.4), etiquetas=[(-72.35, 19.2, "HAITÍ"), (-70.9, 18.95, "REPÚBLICA\nDOMINICANA")]),
]

# Ficha de datos que se muestra bajo el mapa en cada escena (líneas de <= 40 caracteres)
FICHAS = [
    ["7 invasiones · 1801–1856", "2 tomaron Santo Domingo · 5 fracasaron", "Cifras: casi todas, de fuentes dominicanas"],
    ["1795: Tratado de Basilea", "España cede el este a Francia", "1801: el este sigue siendo español"],
    ["Jefe: Toussaint Louverture", "Mandos: Moïse y Paul Louverture", "Fecha: 4 al 26 de enero de 1801", "Ruta: dos cuerpos de ejército (esquema)", "Pretexto: Francia no había tomado", "posesión del este (Basilea)"],
    ["Resultado: toma Santo Domingo", "Resistencia: escasa", "Esclavitud: las fuentes discrepan", "Fin: 1802, expedición francesa"],
    ["Jefes: Dessalines y Christophe", "Tropas: más de 20.000 (una fuente)", "Detonante: proclama de Ferrand", "(6 de enero de 1805)"],
    ["Christophe: Cibao (Santiago, Moca,", "La Vega)", "Dessalines: sitio de Santo Domingo", "desde el 5 de marzo", "Fin: llega escuadra francesa"],
    ["Retirada: pueblos destruidos", "Muertes: ~10.000 (cifra muy variable)", "Peores casos: Moca y Santiago", "Fuentes secundarias: con cautela"],
    ["Jefe: Jean-Pierre Boyer", "1 dic 1821: Estado del Haití Español", "Pueblos fronterizos piden unirse", "a Haití"],
    ["20 de enero al 9 de febrero de 1822", "Bonnet: Dajabón, Santiago, La Vega", "Boyer: ~12.000 hombres, 2 columnas", "6 feb: Baní · 9 feb: Santo Domingo"],
    ["Combates: no constan en las fuentes", "consultadas", "Duración del dominio: 22 años"],
    ["27 de febrero de 1844: independencia", "Tropas haitianas: 20.000–30.000", "(una fuente: 40.000)", "Tres columnas"],
    ["Norte: Pierrot (Dajabón → Santiago)", "Centro: Hérard (San Juan → Azua)", "Sur: Souffrand (por Neiba)", "Las fuentes discrepan en el reparto"],
    ["13 mar: Fuente del Rodeo", "19 mar: Azua", "Dominicanos ~2.200 · haitianos ~10.000", "Bajas (bando vencedor): ~1.000 y 2"],
    ["30 mar: Santiago (Imbert)", "Dominicanos ~3.000 · haitianos ~10.000", "Pierrot se retira: impreso falso", "Perseguido hasta cerca de Dajabón"],
    ["15 abr: Tortuguero", "3 may: cae Hérard en Haití", "La invasión dura menos de un mes"],
    ["Presidente haitiano: Pierrot", "22 jul: expulsa a los dominicanos", "de Cachimán", "6 ago: ordena invadir"],
    ["17 sep: Estrelleta (Duvergé)", "27 oct: Beler, fuerte «El Invencible»", "Retirada por el río Dajabón"],
    ["Jefe: Faustin Soulouque", "Tropas: ~18.000", "Ruta: Las Matas → San Juan → Azua", "Llega al río Ocoa (~86 km de la capital)"],
    ["17 abr: El Número (Duvergé)", "~21 abr: Las Carreras (Santana)", "Bajas: Haití, más del doble (una fuente)"],
    ["Jefe: Soulouque (Faustin I)", "Tropas: 12.000 a 30.000", "3 cuerpos: Dajabón, Las Matas, Neiba", "Reorganización: noviembre de 1855"],
    ["22 dic: Santomé (Cabral)", "22 dic: Cambronal (Sosa)", "Sabana Larga (Franco Bidó): ~8.000", "contra ~22.000 · fecha: dic 1855 o", "24 ene 1856"],
    ["Tomaron Santo Domingo: 1801 y 1822", "Fracasaron: 1805, 1844, 1845,", "1849 y 1855–56"],
    ["Tesis de la unificación (interpretación)", "Pretextos legales · rivalidad con Francia", "Ambición de poder · llamamientos", "fronterizos", "Derrotas: abastecimiento, terreno, política"],
    ["Cifras: casi todas de fuentes dominicanas", "Falta contrastar con historiografía", "haitiana", "Lugares y rutas, aproximados"],
    ["7 invasiones", "12 años de guerra tras la independencia", "dominicana"],
]
assert len(FICHAS) == len(SCENES), (len(FICHAS), len(SCENES))
for _sc, _f in zip(SCENES, FICHAS):
    _sc["ficha"] = _f
