# Guiones narrados: shorts de mapas

Tono: narrador de documental, cercano y con intriga. Ritmo pausado, unas 150 palabras por minuto.
`[pausa]` = medio segundo de silencio. Las palabras en **negrita** van con énfasis.
Los tiempos coinciden con los vídeos y mapas ya generados.

---

## 1. Gibraltar: «Un trozo de Reino Unido pegado a España»

Encaja con `short_gibraltar/gibraltar_short.mp4`.

| Tiempo | Voz narrativa | En pantalla |
|---|---|---|
| 0–6 s | Mira bien este mapa. [pausa] Esto es España… pero en la punta de abajo hay algo que **no** es España. | Europa → España en amarillo |
| 6–13 s | Bajamos hasta el Estrecho, el punto donde Europa casi toca África… y donde el Atlántico se abre al Mediterráneo. | Estrecho, Marruecos, Ceuta |
| 13–22 s | Y ahí está. [pausa] **Gibraltar.** Una roca de menos de siete kilómetros cuadrados… con bandera británica. | Zoom a Gibraltar |
| 22–31 s | Todo empezó en 1704. España estaba en plena guerra por su trono… y una flota inglesa y holandesa aprovechó para tomar el peñón. | «1704» |
| 31–40 s | Nueve años después, el Tratado de Utrecht lo hizo oficial: Gibraltar pasaba a Gran Bretaña… [pausa] **«para siempre».** | «1713 · Tratado de Utrecht» |
| 40–46 s | España nunca lo aceptó. Pero cuando se preguntó a los gibraltareños, en 1967 y en 2002… votaron seguir siendo británicos. | «1967 · Referéndum» |
| 46–52 s | En 1969, España cerró la frontera. [pausa] Dieciséis años de verja cerrada… hasta 1985. | Verja en rojo |
| 52–60 s | Y en julio de 2026, un acuerdo entre Europa y el Reino Unido hizo lo impensable: **quitar la verja**. [pausa] Gibraltar sigue siendo británico… pero la frontera, ya casi no existe. | La verja desaparece |

### Texto limpio para grabar o pasar a una voz sintética

> Mira bien este mapa. Esto es España… pero en la punta de abajo hay algo que no es España.
> Bajamos hasta el Estrecho, el punto donde Europa casi toca África… y donde el Atlántico se abre al Mediterráneo.
> Y ahí está. Gibraltar. Una roca de menos de siete kilómetros cuadrados… con bandera británica.
> Todo empezó en 1704. España estaba en plena guerra por su trono… y una flota inglesa y holandesa aprovechó para tomar el peñón.
> Nueve años después, el Tratado de Utrecht lo hizo oficial: Gibraltar pasaba a Gran Bretaña… «para siempre».
> España nunca lo aceptó. Pero cuando se preguntó a los gibraltareños, en 1967 y en 2002… votaron seguir siendo británicos.
> En 1969, España cerró la frontera. Dieciséis años de verja cerrada… hasta 1985.
> Y en julio de 2026, un acuerdo entre Europa y el Reino Unido hizo lo impensable: quitar la verja. Gibraltar sigue siendo británico… pero la frontera, ya casi no existe.

---

## 2. Bolivia: «Un país sin mar… con Armada»

Encaja con los mapas de `short_bolivia_mapas/`.

| Tiempo | Voz narrativa | Mapa |
|---|---|---|
| 0–4 s | Este país no tiene ni un metro de costa… [pausa] y aun así tiene **Armada**. | `01_gancho_sudamerica.png` |
| 4–12 s | Pero no siempre fue así. En 1879, Bolivia llegaba hasta el Pacífico, con su propio puerto: Antofagasta. | `02_bolivia_1879.png` |
| 12–24 s | Ese año estalló la Guerra del Pacífico. Bolivia y Perú contra Chile. [pausa] Y Chile **ganó**. | Fundido de `02` a `03` |
| 24–32 s | En 1904, un tratado lo dejó por escrito: la costa pasaba a Chile. Bolivia se quedaba encerrada entre montañas. | `03_hoy_sin_costa.png` |
| 32–46 s | ¿Y la Armada? [pausa] Sus marinos patrullan ríos de la Amazonía… y el lago Titicaca, el lago navegable más alto del mundo, a casi cuatro mil metros de altura. | `04_titicaca.png` → `05_rios_y_lagos.png` |
| 46–54 s | Cada 23 de marzo, Bolivia celebra el Día del Mar… y vuelve a reclamar su salida al océano. | `03_hoy_sin_costa.png` |
| 54–60 s | En 2018, la Corte de La Haya dijo que Chile no estaba obligado a negociar. [pausa] El mar sigue ahí… al otro lado de la frontera. | `03_hoy_sin_costa.png` |

### Texto limpio para grabar o pasar a una voz sintética

> Este país no tiene ni un metro de costa… y aun así tiene Armada.
> Pero no siempre fue así. En 1879, Bolivia llegaba hasta el Pacífico, con su propio puerto: Antofagasta.
> Ese año estalló la Guerra del Pacífico. Bolivia y Perú contra Chile. Y Chile ganó.
> En 1904, un tratado lo dejó por escrito: la costa pasaba a Chile. Bolivia se quedaba encerrada entre montañas.
> ¿Y la Armada? Sus marinos patrullan ríos de la Amazonía… y el lago Titicaca, el lago navegable más alto del mundo, a casi cuatro mil metros de altura.
> Cada 23 de marzo, Bolivia celebra el Día del Mar… y vuelve a reclamar su salida al océano.
> En 2018, la Corte de La Haya dijo que Chile no estaba obligado a negociar. El mar sigue ahí… al otro lado de la frontera.

---

Las fuentes de cada dato están en `short_gibraltar/guion.md` y en la conversación del short de Bolivia.

## Versión usada en las voces generadas (`voces/`)

Para que cada frase quepa en su escena, la voz sintética usa versiones más cortas de cuatro frases:

- Gibraltar, 40–46 s: «En 1967, y en 2002, Gibraltar votó seguir siendo británico.»
- Gibraltar, 46–52 s: «En 1969, España cerró la frontera… hasta el ochenta y cinco.»
- Gibraltar, 52–60 s: «En julio de 2026, un acuerdo con Europa quitó la verja. Gibraltar sigue siendo británico… pero ya sin verja.»
- Bolivia, 54–60 s: «En 2018, La Haya falló a favor de Chile. El mar sigue al otro lado.»

En Bolivia, «a casi cuatro mil metros» se cambió por «en lo alto de los Andes», porque esa cifra no está confirmada en las fuentes.

Voces: Kokoro 82M (Apache 2.0), voces en español `em_alex` (hombre) y `ef_dora` (mujer). Se generan con `voces/narrar.py`.
