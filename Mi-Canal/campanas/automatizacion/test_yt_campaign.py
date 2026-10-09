import json, os, tempfile, unittest, datetime as dt
from pathlib import Path
import yt_campaign as y

class T(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        y.QUEUE, y.STATE = self.d / "q.json", self.d / "s.json"
        self.calls = []
        self.vid_desc = "vieja"
        for k in ("YT_BYRABIT_CLIENT_ID", "YT_BYRABIT_CLIENT_SECRET", "YT_BYRABIT_REFRESH_TOKEN"):
            os.environ[k] = "x"
        y.call = self.fake
        item = {"id": "a", "artista": "byrabit", "accion": "set_description", "cuando": "2020-01-01T00:00:00Z",
                "aprobado": True, "video_id": "V", "texto": "NUEVO"}
        y.save(y.QUEUE, {"elementos": [item]})

    def fake(self, m, url, token=None, body=None, headers=None, raw=None):
        self.calls.append((m, url))
        if "oauth2" in url: return 200, {"access_token": "t"}, {}
        if "channels?part=id" in url: return 200, {"items": [{"id": self.chan}]}, {}
        if m == "GET" and "videos?part=snippet" in url:
            return 200, {"items": [{"snippet": {"channelId": self.chan, "title": "t", "categoryId": "10", "description": self.vid_desc}}]}, {}
        if m == "PUT":
            self.vid_desc = body["snippet"]["description"]; return 200, {}, {}
        return 404, {}, {}
    chan = "UCjzieK38GAFid-LW7dzHQJQ"
    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)

    def test_dry_run_no_escribe(self):
        y.publish(False, self.now)
        self.assertFalse(any(m == "PUT" for m, _ in self.calls))

    def test_live_escribe_una_vez(self):
        y.publish(True, self.now); y.publish(True, self.now)
        self.assertEqual(sum(m == "PUT" for m, _ in self.calls), 1)
        self.assertTrue(self.vid_desc.startswith("NUEVO"))

    def test_canal_incorrecto_no_actua(self):
        self.chan = "OTRO"
        y.publish(True, self.now)
        self.assertFalse(any(m == "PUT" for m, _ in self.calls))

    def test_no_aprobado_o_futuro(self):
        q = y.load(y.QUEUE, {}); q["elementos"][0]["aprobado"] = False; y.save(y.QUEUE, q)
        y.publish(True, self.now)
        self.assertFalse(any(m == "PUT" for m, _ in self.calls))

    def test_sin_secretos_bloquea_una_vez(self):
        del os.environ["YT_BYRABIT_REFRESH_TOKEN"]
        y.publish(True, self.now)
        self.assertEqual(y.load(y.STATE, {})["a"]["estado"], "bloqueado")

if __name__ == "__main__":
    unittest.main()
