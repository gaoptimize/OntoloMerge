#!/usr/bin/env python3
"""serve_ontolomerge.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""

import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parent / "sumo_lcc_map.sqlite"
if not DB.exists():
    DB = HERE.parent / "data" / "ontolomerge_public.sqlite"
MODSOURCE = "ontolomerge_github_editor_v0_3_20261103"
HOST, PORT = "127.0.0.1", 41771

RELATIONS = {"exact", "broader", "narrower", "partial", "generic",
             "related", "none"}
ACTIONS = {"create", "modify", "delete"}
INITIALS = re.compile(r"^[A-Za-z]{2,4}$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS provisional_link (
  id INTEGER PRIMARY KEY,
  sumo_term TEXT NOT NULL,
  lcc_row_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  direction TEXT NOT NULL,
  initials TEXT NOT NULL,
  note TEXT,
  action TEXT NOT NULL DEFAULT 'create',
  status TEXT NOT NULL DEFAULT 'provisional',
  created_utc TEXT NOT NULL,
  decided_utc TEXT,
  decided_by TEXT,
  modsource TEXT NOT NULL
)
"""


def db():
    if not DB.is_file():
        raise FileNotFoundError(f"mapping database not found: {DB}")
    con = sqlite3.connect(str(DB))
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(SCHEMA)
    return con


def artifact():
    # modsource: codex_ontolomerge_v04_20261105
    active = HERE / 'current_release.json'
    if active.is_file():
        filename = json.loads(active.read_text(encoding='utf8'))['artifact']
        if Path(filename).name != filename:
            raise ValueError('Active artifact must be a filename in the viewer folder')
        page = HERE / filename
        if not page.is_file():
            raise FileNotFoundError(page)
        return page
    pages = sorted(HERE.glob("ontolomerge_v0_1_*.html"))
    if not pages:
        pages = sorted(HERE.parent.glob("ontolomerge_v0_1_*.html"))
    if not pages:
        sys.exit("no exported page found - run export_ontolomerge_data.py first")
    return pages[-1]


DIRECTIONS = {"S2L", "L2S"}


def direction_ok(payload):
    """create/modify address one side, so they keep the strict single
    direction. delete retires the link as a whole, so it also accepts the
    stored composite of a two-way link ("L2S,S2L" either order)."""
    d = payload.get("direction")
    if d in DIRECTIONS:
        return True
    if payload.get("action") == "delete" and isinstance(d, str):
        parts = d.split(",")
        return all(p in DIRECTIONS for p in parts)
    return False


def validate(con, payload):
    errs = []
    s, l = payload.get("sumo", ""), payload.get("lcc", "")
    known = con.execute("SELECT 1 FROM node WHERE scheme='SUMO' AND node_id=?", (s,)).fetchone()
    if not known and (HERE / 'current_release.json').is_file():
        config = json.loads((HERE / 'current_release.json').read_text(encoding='utf8'))
        filename = config.get('catalog', '')
        if filename and Path(filename).name == filename and (HERE / filename).is_file():
            with sqlite3.connect((HERE / filename).as_uri() + '?mode=ro', uri=True) as catalog:
                known = catalog.execute('SELECT 1 FROM class_symbol WHERE name=? AND reachable=1', (s,)).fetchone()
            catalog.close()
    if not known:
        errs.append(f"unknown SUMO class {s!r}")
    if not con.execute("SELECT 1 FROM node WHERE scheme='LCC' AND node_id=?",
                       (l,)).fetchone():
        errs.append(f"unknown LCC row {l!r}")
    if payload.get("relation") not in RELATIONS:
        errs.append("relation must be one of " + ",".join(sorted(RELATIONS)))
    if not direction_ok(payload):
        errs.append("direction must be S2L or L2S")
    if payload.get("action") not in ACTIONS:
        errs.append("action must be create|modify|delete")
    if not INITIALS.match(payload.get("initials", "")):
        errs.append("initials must be 2-4 letters")
    return errs


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            return self._json({"ok": True, "mode": "workbench",
                               "modsource": MODSOURCE})
        if self.path == "/api/provisional":
            con = db()
            rows = con.execute(
                "SELECT id, sumo_term, lcc_row_id, relation, direction,"
                " initials, note, action, created_utc"
                " FROM provisional_link WHERE status='provisional'"
                " ORDER BY id").fetchall()
            con.close()
            cols = ["id", "sumo", "lcc", "relation", "direction",
                    "initials", "note", "action", "created_utc"]
            return self._json({"rows": [dict(zip(cols, r)) for r in rows]})
        if self.path in ("/", "/index.html"):
            body = artifact().read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/propose":
            return self._json({"error": "not found"}, 404)
        try:
            payload = json.loads(self.rfile.read(
                int(self.headers.get("Content-Length", 0))))
        except (ValueError, KeyError):
            return self._json({"error": "bad json"}, 400)
        con = db()
        errs = validate(con, payload)
        if errs:
            con.close()
            return self._json({"error": "; ".join(errs)}, 422)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur = con.execute(
            "INSERT INTO provisional_link (sumo_term, lcc_row_id, relation,"
            " direction, initials, note, action, status, created_utc,"
            " modsource) VALUES (?,?,?,?,?,?,?,'provisional',?,?)",
            (payload["sumo"], payload["lcc"], payload["relation"],
             payload["direction"], payload["initials"].upper(),
             payload.get("note", ""), payload["action"], now, MODSOURCE))
        con.commit()
        rid = cur.lastrowid
        con.close()
        self._json({"ok": True, "id": rid, "created_utc": now,
                    "status": "provisional"})


def main():
    con = db()
    con.close()
    print(f"OntoloMerge workbench on http://{HOST}:{PORT}/")
    print(f"serving {artifact().name}; writes -> provisional_link only")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
