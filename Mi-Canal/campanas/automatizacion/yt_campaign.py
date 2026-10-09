#!/usr/bin/env python3
"""Automatización gratuita de la campaña musical (solo biblioteca estándar).

Comandos:
  authorize <artista>   (en TU ordenador) consentimiento OAuth y refresh token
  check                 comprueba credenciales y que el canal sea el correcto
  publish [--live]      ejecuta elementos aprobados y vencidos de cola.json
  report [--days N]     guarda métricas en metricas.csv e informe_ultimo.md

Seguridad: por defecto no escribe nada en YouTube (simulación). Solo actúa en
modo --live (o CAMPANA_LIVE=1), si el canal autenticado coincide con
config.json, el elemento está aprobado y no hay un resultado previo ni ambiguo.
No usa contraseñas ni OTP: solo tokens OAuth que el propietario autoriza.
"""
import argparse, base64, csv, datetime as dt, hashlib, http.server, json, os
import secrets, sys, urllib.error, urllib.parse, urllib.request, webbrowser
from pathlib import Path

HERE = Path(__file__).parent
CFG, QUEUE, STATE = HERE / "config.json", HERE / "cola.json", HERE / "estado.json"
METRICS, REPORT = HERE / "metricas.csv", HERE / "informe_ultimo.md"
SCOPES = ("https://www.googleapis.com/auth/youtube "
          "https://www.googleapis.com/auth/yt-analytics.readonly")
API = "https://www.googleapis.com/youtube/v3"


class Bloqueo(Exception):
    pass


def call(method, url, token=None, body=None, headers=None, raw=None):
    h = dict(headers or {})
    if token:
        h["Authorization"] = "Bearer " + token
    data = raw
    if body is not None:
        data = json.dumps(body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read()
            return r.status, (json.loads(txt) if txt[:1] in b"{[" else {}), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:500]}, {}


def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def save(p, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def creds(art, cfg):
    a = cfg["artistas"][art]
    if not a.get("admin_verificada"):
        raise Bloqueo("administración del canal sin verificar")
    vals = [os.environ.get(k) for k in a["secretos_env"]]
    if not all(vals):
        raise Bloqueo("faltan secretos: " + ", ".join(a["secretos_env"]))
    return vals


def access_token(art, cfg):
    cid, sec, rt = creds(art, cfg)
    body = urllib.parse.urlencode({"client_id": cid, "client_secret": sec,
                                   "refresh_token": rt, "grant_type": "refresh_token"}).encode()
    st, js, _ = call("POST", "https://oauth2.googleapis.com/token", raw=body,
                     headers={"Content-Type": "application/x-www-form-urlencoded"})
    if st != 200 or "access_token" not in js:
        raise Bloqueo(f"token rechazado ({st})")
    return js["access_token"]


def verify_owner(art, cfg, tok):
    st, js, _ = call("GET", f"{API}/channels?part=id&mine=true", tok)
    ids = [i["id"] for i in js.get("items", [])] if st == 200 else []
    if cfg["artistas"][art]["channel_id"] not in ids:
        raise Bloqueo("el canal autenticado no es el esperado; no se actúa")


def act_set_description(it, cfg, tok, live):
    vid = it["video_id"]
    st, js, _ = call("GET", f"{API}/videos?part=snippet&id={vid}", tok)
    if st != 200 or not js.get("items"):
        raise Bloqueo(f"no se pudo leer el vídeo {vid}")
    sn = js["items"][0]["snippet"]
    if sn["channelId"] != cfg["artistas"][it["artista"]]["channel_id"]:
        raise Bloqueo("el vídeo no pertenece al canal del artista")
    if it["texto"] in sn.get("description", ""):
        return "publicado", f"https://www.youtube.com/watch?v={vid}", "ya contenía el texto"
    if not live:
        return "simulado", "", "no se escribió nada"
    sn["description"] = it["texto"] + "\n\n" + sn.get("description", "")
    for k in ("thumbnails", "channelTitle", "publishedAt", "channelId", "liveBroadcastContent",
              "localized", "publishTime"):
        sn.pop(k, None)
    st, _, _ = call("PUT", f"{API}/videos?part=snippet", tok, {"id": vid, "snippet": sn})
    if st != 200:
        return "ambiguo", "", f"respuesta {st}; revisar el historial antes de repetir"
    st, js, _ = call("GET", f"{API}/videos?part=snippet&id={vid}", tok)
    ok = st == 200 and it["texto"] in js["items"][0]["snippet"].get("description", "")
    return ("publicado" if ok else "ambiguo"), f"https://www.youtube.com/watch?v={vid}", "verificado" if ok else "no verificado"


def act_upload_short(it, cfg, tok, live):
    if not it.get("derechos_confirmados"):
        raise Bloqueo("derechos del clip sin confirmar")
    f = HERE / it["archivo"]
    if not f.is_file():
        raise Bloqueo("no existe el archivo " + it["archivo"])
    st, js, _ = call("GET", f"{API}/channels?part=contentDetails&mine=true", tok)
    up = js["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"] if st == 200 and js.get("items") else None
    if up:
        st, js, _ = call("GET", f"{API}/playlistItems?part=snippet&playlistId={up}&maxResults=50", tok)
        if st == 200 and any(i["snippet"]["title"] == it["titulo"] for i in js.get("items", [])):
            return "ambiguo", "", "ya existe un vídeo con ese título; no se repite"
    if not live:
        return "simulado", "", "no se subió nada"
    meta = {"snippet": {"title": it["titulo"], "description": it.get("descripcion", "")},
            "status": {"privacyStatus": it.get("privacidad", "public"), "selfDeclaredMadeForKids": False}}
    st, _, hd = call("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                     tok, meta, {"X-Upload-Content-Type": "video/*"})
    loc = hd.get("Location")
    if st != 200 or not loc:
        return "ambiguo", "", f"inicio de subida {st}"
    st, js, _ = call("PUT", loc, tok, raw=f.read_bytes(), headers={"Content-Type": "video/*"})
    if st not in (200, 201) or "id" not in js:
        return "ambiguo", "", f"subida {st}; revisar el historial"
    return "publicado", f"https://www.youtube.com/shorts/{js['id']}", "subido"


ACCIONES = {"set_description": act_set_description, "upload_short": act_upload_short}


def publish(live, now=None):
    cfg, q, state = load(CFG, {}), load(QUEUE, {"elementos": []}), load(STATE, {})
    now = now or dt.datetime.now(dt.timezone.utc)
    toks = {}
    for it in q["elementos"]:
        iid = it["id"]
        if not it.get("aprobado"):
            continue
        if state.get(iid, {}).get("estado") in ("publicado", "ambiguo", "simulado_final"):
            continue
        if dt.datetime.fromisoformat(it["cuando"].replace("Z", "+00:00")) > now:
            continue
        art = it["artista"]
        try:
            if art not in toks:
                toks[art] = access_token(art, cfg)
                verify_owner(art, cfg, toks[art])
            est, ev, nota = ACCIONES[it["accion"]](it, cfg, toks[art], live)
        except Bloqueo as e:
            prev = state.get(iid, {})
            if prev.get("nota") != str(e):  # registrar el bloqueo una sola vez
                state[iid] = {"estado": "bloqueado", "nota": str(e), "en": now.isoformat()}
                print(f"BLOQUEADO {iid}: {e}")
            continue
        if est != "simulado":
            state[iid] = {"estado": est, "evidencia": ev, "nota": nota, "en": now.isoformat()}
        print(f"{est.upper()} {iid} {ev} {nota}")
    save(STATE, state)
    return state


def report(days):
    cfg = load(CFG, {})
    end = dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=days - 1)
    new = not METRICS.exists()
    rows = []
    for art, a in cfg["artistas"].items():
        try:
            tok = access_token(art, cfg)
            verify_owner(art, cfg, tok)
        except Bloqueo as e:
            print(f"SIN DATOS {art}: {e}")
            continue
        qs = urllib.parse.urlencode({"ids": "channel==" + a["channel_id"], "startDate": start.isoformat(),
                                     "endDate": end.isoformat(), "dimensions": "video", "sort": "-views",
                                     "maxResults": 50,
                                     "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained"})
        st, js, _ = call("GET", "https://youtubeanalytics.googleapis.com/v2/reports?" + qs, tok)
        if st != 200:
            print(f"SIN DATOS {art}: analytics {st}")
            continue
        for r in js.get("rows", []):
            rows.append([dt.date.today().isoformat(), art, r[0], a["videos"].get(r[0], "otro"),
                         days, r[1], r[2], r[3], r[4]])
    with METRICS.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["fecha", "artista", "video_id", "tipo", "ventana_dias", "vistas",
                        "minutos_vistos", "duracion_media_s", "suscriptores_ganados"])
        w.writerows(rows)
    lines = [f"# Informe ({start} a {end}, {days} días)\n", "Las vistas de clips (short) y de canciones completas se cuentan por separado. Sin datos = sin fila, nunca un cero inventado.\n",
             "| Artista | Tipo | Vistas | Minutos vistos | Suscriptores ganados |", "|---|---|---|---|---|"]
    agg = {}
    for r in rows:
        k = (r[1], r[3])
        v = agg.setdefault(k, [0, 0, 0])
        v[0] += r[5]; v[1] += r[6]; v[2] += r[8]
    for (a, t), v in sorted(agg.items()):
        lines.append(f"| {a} | {t} | {v[0]} | {v[1]} | {v[2]} |")
    if not agg:
        lines.append("| (sin datos) | | | | |")
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def authorize(art):
    """Se ejecuta en TU ordenador: abre el navegador, tú aceptas, y se imprime el refresh token."""
    cid = input("Client ID de OAuth (tipo aplicación de escritorio): ").strip()
    sec = input("Client secret: ").strip()
    ver = secrets.token_urlsafe(64)
    chal = base64.urlsafe_b64encode(hashlib.sha256(ver.encode()).digest()).rstrip(b"=").decode()
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200); self.end_headers()
            self.wfile.write(b"Listo, puedes cerrar esta pestana.")
        def log_message(self, *a): pass
    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redir = f"http://127.0.0.1:{srv.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redir, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "code_challenge": chal, "code_challenge_method": "S256"})
    print("Abre este enlace con la cuenta PROPIETARIA del canal", art, ":\n", url)
    webbrowser.open(url)
    srv.handle_request()
    body = urllib.parse.urlencode({"code": got["code"][0], "client_id": cid, "client_secret": sec,
                                   "redirect_uri": redir, "grant_type": "authorization_code", "code_verifier": ver}).encode()
    st, js, _ = call("POST", "https://oauth2.googleapis.com/token", raw=body,
                     headers={"Content-Type": "application/x-www-form-urlencoded"})
    print("\nGuarda esto como secreto (NO lo pegues en chats ni en el repositorio):\n", js.get("refresh_token", js))


def check():
    cfg = load(CFG, {})
    for art in cfg["artistas"]:
        try:
            tok = access_token(art, cfg); verify_owner(art, cfg, tok)
            print(f"OK {art}: acceso al canal correcto")
        except Bloqueo as e:
            print(f"PENDIENTE {art}: {e}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="c", required=True)
    sp.add_parser("check")
    p = sp.add_parser("publish"); p.add_argument("--live", action="store_true")
    r = sp.add_parser("report"); r.add_argument("--days", type=int, default=28)
    a = sp.add_parser("authorize"); a.add_argument("artista", choices=["byrabit", "taquitos"])
    n = ap.parse_args()
    if n.c == "check": check()
    elif n.c == "publish": publish(n.live or os.environ.get("CAMPANA_LIVE") == "1")
    elif n.c == "report": report(n.days)
    else: authorize(n.artista)
