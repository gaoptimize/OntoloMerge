#!/usr/bin/env python3
"""serve_sumo_editor.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""
import argparse
import json
import re
import secrets
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from serve_ontolomerge import Handler as MappingHandler, artifact
from sumo_editor import MODSOURCE, Workspace

HERE = Path(__file__).resolve().parent


def load_artifact(path):
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r"const DATA = (.*);\s*\n", text)
    if not match:
        raise ValueError("artifact has no data payload")
    return text, json.loads(match[1])


def make_handler(workspace, html, token):
    class Handler(MappingHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/api/health":
                return self._json({"ok": True, "mode": "sumo_editor", "token": token,
                                   "modsource": MODSOURCE})
            if path == "/api/class_edits":
                data = workspace.data()
                return self._json({"rows": workspace.edits(), "revision": data["editor"]["revision"]})
            if path == "/api/sumo_delta.zip":
                try:
                    body = workspace.export()
                except ValueError as exc:
                    return self._json({"error": str(exc)}, 422)
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", 'attachment; filename="ontolomerge-sumo-delta.zip"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path in ("/", "/index.html"):
                data = workspace.data()
                payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
                page = re.sub(r"const DATA = .*;(?=\s*\n)", lambda _: "const DATA = " + payload + ";", html, count=1)
                ui = (HERE / "sumo_editor_ui.js").read_text(encoding="utf-8")
                page = page.replace("// ---------- go ----------", ui + "\n// ---------- go ----------")
                page = page.replace("edits → provisional_link", "SUMO editor · local workspace")
                body = page.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            return super().do_GET()

        def do_POST(self):
            # JSON + origin check protects even the inherited mapping endpoint.
            expected = "http://" + self.headers.get("Host", "")
            if self.headers.get("Origin", expected) != expected or\
                    self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self._json({"error": "same-origin JSON request required"}, 403)
            if self.headers.get("Host") not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
                return self._json({"error": "invalid host"}, 403)
            if self.path == "/api/propose":
                return super().do_POST()
            if self.headers.get("X-OntoloMerge-Token") != token:
                return self._json({"error": "editor session expired; refresh page"}, 403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 100000:
                    raise ValueError("request must be 1–100000 bytes")
                p = json.loads(self.rfile.read(length))
                if not isinstance(p, dict):
                    raise ValueError("expected a JSON object")
                if self.path == "/api/preview_class_edit":
                    _, summary = workspace.preview(p)
                    return self._json({"summary": summary, "revision": workspace.row()["revision"]})
                if self.path == "/api/propose_class_edit":
                    return self._json(workspace.propose(p))
                if self.path == "/api/decide_class_edit":
                    return self._json(workspace.decide(p.get("id"), p.get("decision"), p.get("initials"), p.get("revision")))
                if self.path == "/api/editor_shutdown":
                    import threading
                    self._json({"ok": True})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                    return
                return self._json({"error": "not found"}, 404)
            except (ValueError, TypeError, KeyError) as exc:
                return self._json({"error": str(exc)}, 422)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=41772)
    parser.add_argument("--workspace", type=Path, default=HERE / "editor_workspace" / "sumo_editor.sqlite")
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--check", action="store_true", help="dry run: validate sources and snapshot without creating a workspace")
    args = parser.parse_args()
    if not 10000 < args.port < 65536:
        parser.error("choose an unassigned ephemeral port above 10000")
    html, baseline = load_artifact(args.artifact or artifact())
    # Preserve source line endings: hashes and unified diffs must match the
    # actual Windows checkout, not a silently normalized LF copy.
    sources = {p.name: p.read_bytes().decode("utf-8") for p in sorted((HERE.parent / "sumo_src").glob("*.kif"))}
    if not sources:
        parser.error("vendored SUMO KIF sources are required")
    if args.check:
        from sumo_editor import derive, source_index
        import copy
        parents, _ = source_index(sources)
        depth_parents, _ = source_index({"Merge.kif": sources["Merge.kif"]})
        derive(copy.deepcopy(baseline["sumo_nodes"]), depth_parents)
        print(f"Dry run PASS: {len(baseline['sumo_nodes'])} mapped-tree classes, {len(sources)} KIF files, {len(parents)} KIF subclass subjects. No writes.")
        return
    workspace = Workspace(args.workspace, baseline, sources)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(workspace, html, secrets.token_urlsafe(32)))
    print(f"OntoloMerge SUMO editor: http://127.0.0.1:{server.server_port}/", flush=True)
    print(f"Workspace: {args.workspace}; published mapping and KIF are read-only.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
