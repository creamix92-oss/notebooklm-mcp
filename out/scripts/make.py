import math, sys
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 720, 1280, 2, 24
DUR = 35.2
INK = (34, 34, 34); GRAY = (150, 150, 150)
RED = (226, 62, 62); GREEN = (46, 160, 100); GOLD = (232, 170, 30); BLUE = (60, 110, 220)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_f = {}
def font(sz, bold=True):
    k = (sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(FB if bold else FR, int(sz * S))
    return _f[k]

def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def prog(t, a, b): return ease((t - a) / (b - a))
def lerp(a, b, u): return a + (b - a) * u
def fmt(n): return f"{int(round(n)):,}".replace(",", ".")

class P:
    def __init__(s):
        s.im = Image.new("RGB", (W * S, H * S), "white"); s.d = ImageDraw.Draw(s.im)
    def line(s, pts, c=INK, w=5):
        pts = [(x * S, y * S) for x, y in pts]
        s.d.line(pts, fill=c, width=int(w * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = w * S / 2; s.d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    def circ(s, x, y, r, c=INK, w=5, fill=None):
        s.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=c if w else None, width=int(w * S), fill=fill)
    def rect(s, x0, y0, x1, y1, c=INK, w=5, fill=None, r=0):
        s.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, outline=c if w else None, width=int(w * S), fill=fill)
    def poly(s, pts, c=INK, w=5, fill=None):
        s.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)
        if w: s.line(pts + [pts[0]], c, w)
    def text(s, x, y, t, sz, c=INK, bold=True, anchor="mm"):
        s.d.text((x * S, y * S), t, font=font(sz, bold), fill=c, anchor=anchor)
    def wrap(s, x, y, t, sz, c=INK, maxw=600, bold=True, lh=1.3):
        f = font(sz, bold); lines = []; cur = ""
        for w_ in t.split():
            tr = (cur + " " + w_).strip()
            if f.getlength(tr) / S <= maxw: cur = tr
            else: lines.append(cur); cur = w_
        lines.append(cur)
        for i, l in enumerate(lines): s.text(x, y + i * sz * lh, l, sz, c, bold)
    def pie(s, x, y, r, a0, a1, c):
        s.d.pieslice([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], a0 - 90, a1 - 90, fill=c)

def coin(p, x, y, r=22):
    p.circ(x, y, r, INK, 4, fill=(255, 244, 205)); p.text(x, y + 1, "$", r * 1.1, (190, 130, 10))

def bank(p, x, y):
    w = 130
    p.poly([(x - w - 20, y - 150), (x, y - 220), (x + w + 20, y - 150)], INK, 5)
    for i in range(4):
        cx = x - w + 22 + i * (w * 2 - 44) / 3
        p.rect(cx - 14, y - 135, cx + 14, y - 40, INK, 4)
    p.rect(x - w - 20, y - 36, x + w + 20, y, INK, 5)
    p.circ(x, y - 180, 12, INK, 3); p.text(x, y - 180, "$", 15)

def face(p, x, y, r, mood):
    p.circ(x, y, r, INK, 5, fill="white")
    ex = r * 0.38; ey = y - r * 0.12
    p.circ(x - ex, ey, 4, INK, 0, fill=INK); p.circ(x + ex, ey, 4, INK, 0, fill=INK)
    if mood == "angry":
        p.line([(x - ex - 12, ey - 14), (x - ex + 10, ey - 6)], RED, 5); p.line([(x + ex + 12, ey - 14), (x + ex - 10, ey - 6)], RED, 5)
        p.line([(x - 14, y + r * 0.5), (x, y + r * 0.35), (x + 14, y + r * 0.5)], RED, 5)
    elif mood == "sad":
        p.line([(x - ex - 10, ey - 12), (x - ex + 8, ey - 18)], INK, 4); p.line([(x + ex + 10, ey - 12), (x + ex - 8, ey - 18)], INK, 4)
        p.line([(x - 14, y + r * 0.55), (x, y + r * 0.38), (x + 14, y + r * 0.55)], INK, 5)
    elif mood == "happy":
        p.line([(x - 16, y + r * 0.3), (x, y + r * 0.55), (x + 16, y + r * 0.3)], GREEN, 5)
    else:
        p.line([(x - 12, y + r * 0.45), (x + 12, y + r * 0.45)], INK, 5)

def person(p, x, y, mood="neutral", arms=None, c=INK, bob=0, head_dx=0):
    y += bob
    hy = y - 175
    p.line([(x, hy + 34), (x, y - 70)], c, 6)
    p.line([(x, y - 70), (x - 28, y)], c, 6); p.line([(x, y - 70), (x + 28, y)], c, 6)
    a = arms or ((x - 40, y - 85), (x + 40, y - 85))
    p.line([(x, y - 125), a[0]], c, 6); p.line([(x, y - 125), a[1]], c, 6)
    face(p, x + head_dx, hy, 34, mood)

def clock(p, x, y, r, wedge=0.0, hand=0.0):
    p.circ(x, y, r, INK, 6, fill="white")
    if wedge > 0: p.pie(x, y, r - 8, 0, 360 * wedge, (250, 205, 205))
    for i in range(12):
        a = math.radians(i * 30); p.line([(x + math.sin(a) * (r - 14), y - math.cos(a) * (r - 14)), (x + math.sin(a) * (r - 4), y - math.cos(a) * (r - 4))], INK, 4)
    a = math.radians(hand * 360); p.line([(x, y), (x + math.sin(a) * (r - 30), y - math.cos(a) * (r - 30))], INK, 6)
    p.circ(x, y, 7, INK, 0, fill=INK)

def counter(p, label, val, c=INK, y=170):
    p.text(W / 2, y - 62, label, 24, GRAY)
    p.text(W / 2, y, fmt(val), 76, c)

def trash(p, x, y):
    p.poly([(x - 55, y - 100), (x + 55, y - 100), (x + 42, y), (x - 42, y)], INK, 5)
    p.line([(x - 65, y - 108), (x + 65, y - 108)], INK, 6)
    for dx in (-18, 0, 18): p.line([(x + dx, y - 85), (x + dx * 0.8, y - 20)], GRAY, 3)

def bar(p, y, frac, c=INK):
    x0, x1 = 80, 640
    p.rect(x0, y, x1, y + 44, INK, 4, r=10)
    if frac > 0.02: p.rect(x0 + 4, y + 4, x0 + 4 + (x1 - x0 - 8) * frac, y + 40, None, 0, fill=c, r=8)

def cloud(p, cx, cy, k):
    for dx, dy, r in ((-40, 0, 46), (10, -22, 56), (62, 4, 44)):
        p.circ(cx + dx, cy + dy, max(1, r * k), GRAY, 0, fill=(205, 205, 210))

# ---------------- scenes ----------------
def s1(p, t, u):
    bank(p, 300, 700)
    counter(p, "EN TU BANCO", prog(t, 0.3, 2.6) * 86400, INK)
    for i in range(int(prog(t, 0.2, 2.6) * 7)): coin(p, 520 + (i % 2) * 6, 700 - i * 14 - 20, 24)

def s2(p, t, u):
    drop = prog(t, 5.0, 5.6)
    bank(p, 300, 700)
    for i in range(7 - (1 if t > 5.0 else 0)): coin(p, 520 + (i % 2) * 6, 700 - i * 14 - 20, 24)
    counter(p, "EN TU BANCO", 86400 - 80 * drop, RED if drop > 0 else INK)
    enter = prog(t, 3.6, 4.7); leave = prog(t, 5.0, 6.7)
    tx = lerp(820, 610, enter) + lerp(0, 260, leave)
    person(p, tx, 700, "angry", ((tx - 55, 610), (tx + 40, 610)), RED, bob=math.sin(t * 14) * 4 * leave)
    p.rect(tx - 36, 700 - 215, tx + 36, 700 - 196, None, 0, fill=INK, r=6)
    if t > 5.0:
        v = ease((t - 5.0) / 0.4); coin(p, lerp(520, tx - 58, v), lerp(670, 612, v), 20)
    if t > 5.3: p.text(W / 2, 290, "− 80 $", 60 + prog(t, 5.3, 5.9) * 8, RED)

def s3(p, t, u):
    counter(p, "LO QUE QUEDA", 86320 * (1 - prog(t, 8.8, 11.6)), INK)
    shake = math.sin(t * 40) * 3
    person(p, 260 + shake, 760, "angry", ((200, 650), (330, 690)), RED)
    trash(p, 590, 760)
    if t < 8.0:
        for k in range(7): coin(p, 335 + (k % 2) * 8, 700 - k * 12, 22)
    for k in range(10):
        a = 8.0 + k * 0.38; v = (t - a) / 0.9
        if 0 <= v < 1:
            v = ease(v); coin(p, lerp(335, 590, v), 695 - math.sin(v * math.pi) * 170, 22)

def s4(p, t, u):
    counter(p, "LO QUE QUEDA", 0, GRAY)
    sh = math.sin(t * 16) * 12 * ease(1 - (t - 12.5) / 1.4)
    person(p, 300, 780, "neutral", ((230, 700), (370, 700)), INK, head_dx=sh)
    p.rect(420, 480, 640, 560, INK, 5, fill="white", r=24); p.text(530, 520, "¡NO!", 44, RED)

def s5(p, t, u):
    w = prog(t, 14.0, 14.8)
    clock(p, W / 2, 620, 190, wedge=w * 0.1, hand=0.0)
    p.text(W / 2, 170, "60 s", 80 * (0.8 + 0.2 * w), RED)
    p.text(W / 2, 108, "UN ROBO MÍNIMO", 24, GRAY)
    p.text(W / 2, 880, "apenas un instante de tu día", 30, GRAY)

def s6(p, t, u):
    n = 86340 * (1 - prog(t, 17.5, 22.5))
    counter(p, "SEGUNDOS QUE TE QUEDAN", n, INK if n > 1000 else RED)
    bar(p, 260, n / 86400, INK)
    person(p, 360, 940, "sad", ((300, 880), (420, 880)), INK)
    k = prog(t, 16.8, 20)
    cloud(p, 360, 640, 0.6 + 0.6 * k)
    for i in range(int(k * 8)):
        x = 300 + i * 18; yy = 700 + ((t * 120 + i * 37) % 110)
        p.line([(x, yy), (x - 4, yy + 16)], BLUE, 4)

def s7(p, t, u):
    back = prog(t, 24.0, 25.3)
    n = 86340 * prog(t, 25.3, 27.3) if t > 25.3 else 0
    counter(p, "SEGUNDOS QUE TE QUEDAN", n, INK if t < 25.3 else GREEN)
    bar(p, 260, n / 86400, GREEN)
    clock(p, 200, 760, 110, wedge=(1 - back) * 0.1)
    p.text(450, 640, "Vamos, devuélvelo…", 32, INK)
    x = lerp(560, 330, back)
    p.rect(x - 70, 780, x + 70, 840, RED, 5, fill="white", r=18); p.text(x, 810, "60 s", 34, RED)
    p.line([(560, 900), (330, 900)], GRAY, 4); p.poly([(322, 900), (348, 886), (348, 914)], GRAY, 0, fill=GRAY)
    if t > 26.0: p.text(W / 2, 1000, "Aún te quedan 86.340 s", 38, GREEN)

def s8(p, t, u):
    k = prog(t, 28.8, 31.0)
    sx = lerp(130, 360, k); sy = lerp(830, 520, k)
    p.circ(sx, sy, 62, GOLD, 0, fill=(255, 219, 110))
    for i in range(12):
        a = math.radians(i * 30); p.line([(sx + math.cos(a) * 80, sy + math.sin(a) * 80), (sx + math.cos(a) * 104, sy + math.sin(a) * 104)], GOLD, 5)
    p.rect(0, 826, W, 940, None, 0, fill="white")
    p.line([(60, 826), (660, 826)], INK, 5)
    cloud(p, 180, 420, 0.1 + 0.9 * (1 - k))
    person(p, 360, 1060, "sad" if k < 0.5 else "happy", ((300, 1000), (420, 1000)), INK)
    bar(p, 220, 0.2 + 0.8 * k, GREEN if k > 0.5 else INK)
    p.text(W / 2, 168, "TU DÍA", 24, GRAY)

def s9(p, t, u):
    k = prog(t, 32.0, 33.2)
    cx, cy = W / 2, 520; r = 130 * (0.85 + 0.15 * k) * (1 + 0.04 * math.sin(t * 6))
    pts = []
    for i in range(0, 360, 6):
        a = math.radians(i); x = 16 * math.sin(a) ** 3; y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * r / 17, cy - y * r / 17))
    p.poly(pts, RED, 6, fill=(255, 225, 225))

SCENES = [
 (0.0, 3.5, s1, "1 · EL PUNTO DE PARTIDA", "Imagina que tienes 86.400 $ en tu cuenta bancaria."),
 (3.5, 6.8, s2, "2 · EL ROBO", "Alguien aparece y te roba solo 80 $."),
 (6.8, 12.5, s3, "3 · LA REACCIÓN ABSURDA", "¿Te enfadarías y tirarías con tus propias manos los 86.320 $ restantes?"),
 (12.5, 13.9, s4, "4 · LA RESPUESTA", "Claro que no."),
 (13.9, 16.4, s5, "5 · LA COMPARACIÓN", "Pero si alguien te quita solo 60 segundos de tu día…"),
 (16.4, 23.5, s6, "6 · EL VERDADERO DAÑO", "…arruinas los 86.340 segundos restantes quedándote de mal humor."),
 (23.5, 28.5, s7, "7 · DEVUÉLVELO", "Aun así, todavía te quedan 86.340 segundos por delante."),
 (28.5, 32.0, s8, "8 · ¿POR QUÉ ARRUINARLO?", "¿Por qué estropear el resto de tu día por algo tan pequeño?"),
 (32.0, 35.3, s9, "9 · LA MORALEJA", "La vida es demasiado corta para desperdiciarla en cosas que no importan."),
]

def frame(t):
    sc = next((x for x in SCENES if x[0] <= t < x[1]), SCENES[-1])
    a, b, fn, tag, cap = sc
    p = P(); fn(p, t, (t - a) / (b - a))
    p.text(W / 2, 60, tag, 22, GRAY)
    last = sc is SCENES[-1]
    if last: p.wrap(W / 2, 800, cap, 44, INK, 580)
    else: p.wrap(W / 2, 1090, cap, 34, INK, 600)
    end = DUR if last else b
    fade = min(1, (t - a) / 0.3, (end - t) / 0.3)
    im = p.im.resize((W, H), Image.LANCZOS)
    if fade < 1: im = Image.blend(Image.new("RGB", (W, H), "white"), im, max(0, fade))
    return im

if __name__ == "__main__":
    import subprocess, os
    D = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        os.makedirs(D + "/t", exist_ok=True)
        for i, t in enumerate([1.5, 5.8, 10.0, 13.0, 14.8, 20.0, 26.5, 30.5, 34.0]): frame(t).save(f"{D}/t/{i}.png")
        sys.exit()
    n = int(DUR * FPS)
    pr = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", sys.argv[1], "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-shortest", sys.argv[2]], stdin=subprocess.PIPE)
    for i in range(n): pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()
