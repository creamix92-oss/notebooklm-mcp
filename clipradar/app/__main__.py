"""Arranque: python -m app"""
import threading
import webbrowser

import uvicorn

from .config import HOST, PORT

if __name__ == "__main__":
    url = f"http://{'localhost' if HOST in ('0.0.0.0', '127.0.0.1') else HOST}:{PORT}"
    print(f"\n  ClipRadar listo en {url}\n")
    import os
    if os.environ.get("CLIPRADAR_NO_BROWSER") != "1":
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run("app.server:app", host=HOST, port=PORT, log_level="warning")
