import math, sys, os, subprocess
from PIL import Image
import make as M
from make import *
import tts

D = os.path.dirname(os.path.abspath(__file__))

def intro(p, t, u):
    k = prog(t, 0, 1.2)
    cx, cy = W / 2, 470
    p.line([(cx - 110, cy - 190), (cx + 110, cy - 190)], INK, 8); p.line([(cx - 110, cy + 190), (cx + 110, cy + 190)], INK, 8)
    p.poly([(cx - 90, cy - 190), (cx + 90, cy - 190), (cx + 8, cy), (cx + 90, cy + 190), (cx - 90, cy + 190), (cx - 8, cy)], INK, 5, fill=None)
    f = (u * 0.8) % 1.0 if True else 0
    top = 170 * (1 - u * 0.9)
    p.poly([(cx - 70 + (170 - top) * 0.3, cy - 40 - top), (cx + 70 - (170 - top) * 0.3, cy - 40 - top), (cx + 6, cy - 6), (cx - 6, cy - 6)], 0, 0, fill=(255, 219, 110))
    p.line([(cx, cy - 6), (cx, cy + 150)], GOLD, 4)
    p.poly([(cx - 70, cy + 186), (cx + 70, cy + 186), (cx, cy + 186 - 20 - 120 * u)], 0, 0, fill=(255, 219, 110))
    p.text(W / 2, 180, "LA VIDA ES CORTA", 50 * (0.9 + 0.1 * k), INK)
    p.text(W / 2, 250, "…y tu tiempo es tu verdadero saldo", 24, GRAY, bold=False)

def day(p, t, u):
    counter(p, "UN DÍA TIENE", 86400 * prog(t, 0.5, 4.5), INK)
    n = int(24 * prog(t, 1.0, 7.0) + 0.001)
    for i in range(24):
        r, c = divmod(i, 6)
        x0 = 90 + c * 92; y0 = 330 + r * 92
        on = i < n
        p.rect(x0, y0, x0 + 80, y0 + 80, GREEN if on else INK, 4, fill=(215, 240, 226) if on else "white", r=12)
        p.text(x0 + 40, y0 + 40, str(i + 1), 26, GREEN if on else GRAY)
    p.text(W / 2, 750, "24 horas", 38, INK)
    p.text(W / 2, 810, "1 hora = 3.600 segundos", 28, GRAY)

def breathe(p, t, u):
    ph = (t % 8) / 8
    r = 90 + 70 * (0.5 - 0.5 * math.cos(ph * 2 * math.pi))
    p.circ(W / 2, 560, r + 26, None, 0, fill=(228, 240, 255)); p.circ(W / 2, 560, r, BLUE, 6, fill=(205, 225, 255))
    p.text(W / 2, 560, "Inhala…" if ph < 0.5 else "Exhala…", 36, BLUE)
    p.text(W / 2, 200, "60 segundos de pausa", 44, INK)
    p.text(W / 2, 270, "respira · reconoce · suelta", 26, GRAY)
    for i, (txt, on) in enumerate((("1 · RESPIRA", u > 0.15), ("2 · NOMBRA LO QUE SIENTES", u > 0.4), ("3 · SUÉLTALO", u > 0.65))):
        p.text(W / 2, 850 + i * 62, txt, 30, GREEN if on else (210, 210, 210))

O = {s[2].__name__: s for s in M.SCENES}
def old(fn): s = O[fn]; return (s[0], s[1], s[2])
LIST = [
 ("intro", intro, None, "0 · INTRODUCCIÓN", "La vida es demasiado corta para desperdiciarla en cosas que no importan.",
  "La vida es demasiado corta para desperdiciarla en cosas que no importan. Veamos por qué, con un ejemplo muy sencillo."),
 ("s1", None, old("s1"), "1 · EL PUNTO DE PARTIDA", "Imagina que cada mañana tienes 86.400 $ en tu cuenta bancaria.",
  "Imagina que cada mañana tienes ochenta y seis mil cuatrocientos dólares en tu cuenta bancaria. Ese es tu saldo."),
 ("s2", None, old("s2"), "2 · EL ROBO", "De pronto, alguien te roba solo 80 $.",
  "De pronto, alguien aparece y te roba solo ochenta dólares. Una pérdida pequeña, comparada con todo lo que tienes."),
 ("s3", None, old("s3"), "3 · LA REACCIÓN ABSURDA", "¿Te enfadarías y tirarías a la basura los 86.320 $ que te quedan?",
  "¿Qué harías? ¿Te pondrías furioso, y tirarías a la basura, con tus propias manos, los ochenta y seis mil trescientos veinte dólares que te quedan?"),
 ("s4", None, old("s4"), "4 · LA RESPUESTA", "Claro que no. Sería absurdo.", "Por supuesto que no. Sería absurdo."),
 ("day", day, None, "5 · TU VERDADERO SALDO", "Cada día tienes 86.400 segundos para gastar.",
  "Pues bien. Un día tiene exactamente ochenta y seis mil cuatrocientos segundos. Ese es tu verdadero saldo diario, y se gasta, te guste o no."),
 ("s5", None, old("s5"), "6 · EL ROBO DE TIEMPO", "Ahora alguien te quita solo 60 segundos.",
  "Ahora, alguien te quita solo sesenta segundos. Un comentario fuera de lugar. Un atasco. Un mensaje molesto."),
 ("s6", None, old("s6"), "7 · EL VERDADERO DAÑO", "Arruinas los 86.340 segundos restantes con mal humor.",
  "Y entonces arruinas los ochenta y seis mil trescientos cuarenta segundos restantes, quedándote de mal humor. Eso sí es tirar tu saldo a la basura."),
 ("s7", None, old("s7"), "8 · DEVUÉLVELO", "Aún tienes 86.340 segundos por delante.",
  "Vamos, devuélvete esos sesenta segundos. Porque todavía tienes ochenta y seis mil trescientos cuarenta segundos por delante."),
 ("breathe", breathe, None, "9 · QUÉ HACER", "Haz una pausa: el mal momento dura un minuto; el mal humor, lo que tú decidas.",
  "La próxima vez, haz una pausa. Respira hondo. Reconoce lo que sientes. Y suéltalo. El mal momento dura un minuto. El mal humor dura, solo si tú lo alimentas."),
 ("s8", None, old("s8"), "10 · ¿POR QUÉ ARRUINARLO?", "¿Por qué estropear el resto de tu día por algo tan pequeño?",
  "¿Por qué estropear el resto de tu día por algo tan pequeño? Deja que salga el sol."),
 ("s9", None, old("s9"), "11 · LA MORALEJA", "La vida es demasiado corta para desperdiciarla en cosas que no importan.",
  "Recuerda. La vida es demasiado corta, para desperdiciarla en cosas que no importan."),
]

def build():
    sc = []; t0 = 0; parts = []
    for i, (name, fn, o, tag, cap, narr) in enumerate(LIST):
        wav = f"{D}/n{i}.wav"; d = tts.synth(narr, wav, rate=145)
        dur = d + (1.0 if i < len(LIST) - 1 else 1.8)
        sc.append((t0, t0 + dur, fn, o, tag, cap)); parts.append((wav, dur)); t0 += dur
    return sc, t0, parts

SC, TOTAL, PARTS = build()

def frame(t):
    s = next((x for x in SC if x[0] <= t < x[1]), SC[-1]); a, b, fn, o, tag, cap = s
    u = (t - a) / (b - a); p = P()
    if fn: fn(p, t - a, u)
    else: o[2](p, o[0] + u * (o[1] - o[0]), u)
    p.text(W / 2, 60, tag, 22, GRAY)
    last = s is SC[-1]
    if last: p.wrap(W / 2, 800, cap, 44, INK, 580)
    else: p.wrap(W / 2, 1090, cap, 34, INK, 600)
    fade = min(1, (t - a) / 0.3, (b - t) / 0.3)
    im = p.im.resize((W, H), Image.LANCZOS)
    if fade < 1: im = Image.blend(Image.new("RGB", (W, H), "white"), im, max(0, fade))
    return im

if __name__ == "__main__":
    out = sys.argv[1]
    print("total", round(TOTAL, 1), [round(b - a, 1) for a, b, *_ in SC])
    if len(sys.argv) > 2 and sys.argv[2] == "test":
        os.makedirs(D + "/t2", exist_ok=True)
        for i, (a, b, *_ ) in enumerate(SC): frame(a + (b - a) * 0.6).save(f"{D}/t2/{i}.png")
        sys.exit()
    # audio: concat narration with silence padding
    ins = []; fl = []
    for i, (w, dur) in enumerate(PARTS):
        ins += ["-i", w]; fl.append(f"[{i}:a]aresample=44100,apad=whole_dur={dur:.3f}[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(PARTS))) + f"concat=n={len(PARTS)}:v=0:a=1,loudnorm[a]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[a]", D + "/narr.wav"], check=True)
    n = int(TOTAL * FPS)
    pr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", D + "/narr.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(n): pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()
