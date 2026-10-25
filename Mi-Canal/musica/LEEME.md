# Instrumentales automáticos para FL Studio

## Qué hay
- `generador.py`: crea un instrumental original (reglas + azar con semilla) como MIDI de 4 pistas (Pad, Bajo, Melodía, Batería), con estructura intro / estrofa / coro / estrofa / coro / final (40 compases).
- Ejemplos: `oracion_D_s7.mid` (68 bpm, re mayor) y `alabanza_G_s3.mid` (82 bpm, sol mayor).
- `*_vista_previa.mp3`: boceto con sonidos sintéticos simples, solo para oír armonía y estructura. No es el sonido final.

## Cómo usarlo en FL Studio
1. Arrastra el `.mid` a la ventana de FL Studio (o File → Import → MIDI file). Importa cada pista como un canal.
2. Asigna a cada canal un instrumento de calidad: pad suave o cuerdas (Pad), bajo sintético o de cuerda (Bajo), piano/eléctrico/guitarra (Melodía), y un kit acústico suave o de percusión (Batería, canal 10 GM).
3. Mezcla, añade reverb y master. El tempo ya viene dentro del MIDI.

## Generar más
`python generador.py --estilo oracion|alabanza --tonalidad C|D|E|F|G|A|B --seed N --salida mi.mid --preview mi.wav`
Cambia la semilla (`--seed`) para otra melodía con los mismos acordes (I–V–vi–IV).

## Honestidad
Probado: los MIDI se generan y se leen bien (cabeceras, pistas, notas, duración 141 s y 117 s). NO puedo escuchar el resultado ni lo he abierto en FL Studio. La calidad "profesional" depende de los instrumentos que cargues y de la mezcla; esto es la base compositiva. Es música original, sin copiar ninguna canción.
