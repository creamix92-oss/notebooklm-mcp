# 📡 ClipRadar

Clipper propio y autoalojado: pegas el enlace de un directo o video (YouTube, Twitch, Kick y
cualquier sitio que soporte yt-dlp), le dices **qué escuchar** y te entrega los shorts ya cortados,
en vertical, con emoji, título y subtítulos.

Todo corre en tu máquina o servidor. No usa APIs de pago ni sube tus videos a ningún lado.

## Qué dispara un clip

| Disparador | Cómo funciona |
|---|---|
| 😂 Risas, 👏 aplausos, 🙌 ovación, 😱 gritos, 🎵 música, 😭 llanto, 💥 explosiones | Modelo YAMNet (521 sonidos de AudioSet) |
| 🗣️ Palabras, frases o nombres | Transcripción con Whisper; ignora mayúsculas/acentos y tolera pequeños errores |
| 🔥 Pico de volumen | Detector propio: sonido muy por encima del nivel de fondo |

Cada disparo guarda *N* segundos antes y *M* después (configurable). Los disparos cercanos se
funden en un solo clip, y en videos grabados se quedan los mejores.

## Arranque

Requisitos: **Python 3.10+**. ffmpeg se instala solo si no lo tienes.
Para YouTube conviene tener **Node.js** o **Deno** instalado (yt-dlp lo usa para resolver los enlaces).

- **Windows:** doble clic en `run.bat`
- **Linux / macOS:** `./run.sh`

Se abre `http://localhost:8787`. La primera vez que uses sonidos o voz se descargan los modelos
(~16 MB sonidos, ~480 MB voz "small") en `data/models`.

## Uso

1. Pega el enlace. **Auto** detecta si es un directo; **En vivo** graba mientras dure y va
   soltando clips en tiempo real hasta que pulses *Detener directo*.
2. Marca los sonidos y añade palabras clave.
3. *Empezar a clipear*. Cada clip se puede reproducir, retitular (re-renderiza), descargar o borrar.
   En videos grabados también puedes crear clips manuales por rango (`1:23` → `1:50`).

## Ajustes (variables de entorno)

| Variable | Por defecto | Uso |
|---|---|---|
| `CLIPRADAR_HOST` | `127.0.0.1` | Pon `0.0.0.0` para abrirlo en tu red/servidor |
| `CLIPRADAR_PORT` | `8787` | Puerto |
| `CLIPRADAR_DATA` | `./data` | Carpeta de trabajos, clips y modelos |
| `CLIPRADAR_NO_BROWSER` | – | `1` para no abrir el navegador (servidores) |

> ⚠️ No tiene login. Si lo expones con `0.0.0.0`, ponlo detrás de una VPN o de un proxy con contraseña.

## Estructura

```
app/audio_events.py  sonidos (YAMNet) y picos de volumen
app/speech.py        Whisper + búsqueda de palabras clave
app/moments.py       agrupa disparos en clips y genera títulos
app/render.py        ffmpeg: 9:16, título con emoji, subtítulos
app/jobs.py          descarga, captura de directos, cola de trabajos
app/server.py        API (FastAPI)    web/index.html  interfaz
```

Usa solo contenido propio o con permiso del creador, y respeta los términos de cada plataforma.
