"""test_sumo_editor.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""
import copy
import hashlib
import io
import json
import tempfile
import subprocess
import sys
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

from serve_sumo_editor import HERE, load_artifact, make_handler
from sumo_editor import Workspace, derive, forms, source_index
from serve_ontolomerge import artifact, DB


def fixture():
    ps = {"Entity": [], "Physical": ["Entity"], "Abstract": ["Entity"],
          "Object": ["Physical"], "Branch": ["Object"], "Leaf": ["Branch"],
          "OtherBranch": ["Object"]}
    nodes = {n: {"label": n, "parents": parents, "doc": n + " doc", "origin": "upstream"} for n, parents in ps.items()}
    derive(nodes)
    source = "\n".join(f"(subclass {n} {p})" for n, parents in ps.items() for p in parents) + "\n"
    source += '\n'.join(f'(documentation {n} EnglishLanguage "{n} doc")' for n in ps) + '\n'
    source += '; (subclass Pretend Fake)\n(documentation Leaf OtherLanguage "do not remove; (subclass Leaf Branch)")\n'
    return {"sumo_nodes": nodes, "links": [{"s": "Leaf", "l": "L1"}], "branches": []}, {"Merge.kif": source}


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        data, self.sources = fixture()
        self.path = Path(self.temp.name) / "workspace.sqlite"
        self.ws = Workspace(self.path, data, self.sources)

    def tearDown(self):
        self.temp.cleanup()

    def payload(self, action="add", **values):
        return dict(action=action, class_name="NewClass", parent="Branch", doc="A local test class.", initials="TST", **values)

    def apply(self, p):
        result = self.ws.propose(p)
        return self.ws.decide(result["id"], "apply", "TST", self.ws.row()["revision"])

    def test_add_preview_apply_backup_and_restart(self):
        p = self.payload()
        result = self.ws.propose(p)
        self.assertNotIn("NewClass", self.ws.data()["sumo_nodes"])
        self.ws.decide(result["id"], "apply", "TS", 0)
        self.assertEqual(self.ws.data()["sumo_nodes"]["NewClass"]["depth"], 4)
        self.assertEqual(len(list((self.path.parent / "backups").glob("*.sqlite"))), 1)
        reopened = Workspace(self.path, {}, {})
        self.assertEqual(reopened.data()["editor"]["revision"], 1)
        self.assertEqual(reopened.sources, self.sources)

    def test_doc_edit_and_real_source_diff(self):
        p = {"action": "edit_doc", "class_name": "Leaf", "doc": 'A "quoted" definition; with (subclass Fake Wrong)\nand a second line.', "initials": "TS"}
        self.apply(p)
        archive = zipfile.ZipFile(io.BytesIO(self.ws.export()))
        patch = archive.read("sumo-changes.patch").decode()
        self.assertIn('-' + '(documentation Leaf EnglishLanguage "Leaf doc")', patch)
        self.assertIn('\\"quoted\\"', patch)
        self.assertEqual(self.sources["Merge.kif"], self.ws.sources["Merge.kif"])
        self.assertEqual(json.loads(archive.read("audit.json"))["round_trip_subclass_sets"], "PASS")

    def test_move_recomputes_and_preserves_secondary_parents(self):
        self.apply(self.payload())
        self.apply({"action": "add", "class_name": "LocalChild", "parent": "NewClass", "extra_parents": ["OtherBranch"], "doc": "Child doc", "initials": "TS"})
        self.apply({"action": "move", "class_name": "NewClass", "parent": "Leaf", "initials": "TS"})
        nodes = self.ws.data()["sumo_nodes"]
        self.assertEqual(nodes["NewClass"]["depth"], 5)
        self.assertEqual(nodes["LocalChild"]["parents"], ["NewClass", "OtherBranch"])
        self.assertEqual(nodes["LocalChild"]["depth"], 4)

    def test_upstream_move_round_trip_removes_real_axiom_only(self):
        self.apply({"action": "move", "class_name": "Leaf", "parent": "OtherBranch", "initials": "TS"})
        archive = zipfile.ZipFile(io.BytesIO(self.ws.export()))
        self.assertIn(b"-(subclass Leaf Branch)", archive.read("sumo-changes.patch"))
        edited = archive.read("edited-kif/Merge.kif").decode()
        self.assertIn('"do not remove; (subclass Leaf Branch)"', edited)
        actual, _ = source_index({name: archive.read(name).decode() for name in archive.namelist() if name.endswith(".kif")})
        self.assertEqual(actual["Leaf"], {"OtherBranch"})

    def test_cycle_rejection_via_secondary_and_hidden_class(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.ws.propose({"action": "move", "class_name": "Branch", "parent": "Leaf", "initials": "TS"})
        data, sources = fixture()
        data["sumo_nodes"]["OtherBranch"]["parents"].append("Hidden")
        sources["Merge.kif"] += "(subclass Hidden Leaf)\n(subclass OtherBranch Hidden)\n"
        ws = Workspace(Path(self.temp.name) / "hidden.sqlite", data, sources)
        with self.assertRaisesRegex(ValueError, "cycle"):
            ws.propose({"action": "move", "class_name": "Leaf", "parent": "OtherBranch", "initials": "TS"})

    def test_restricted_delete_and_rename(self):
        for action in ("delete", "rename"):
            with self.assertRaisesRegex(ValueError, "full axiom audit"):
                self.ws.propose({"action": action, "class_name": "Leaf", "new_name": "OtherLeaf", "initials": "TS"})
        self.apply(self.payload())
        self.apply({"action": "rename", "class_name": "NewClass", "new_name": "RenamedClass", "initials": "TS"})
        self.assertIn("RenamedClass", self.ws.data()["sumo_nodes"])
        self.apply({"action": "delete", "class_name": "RenamedClass", "initials": "TS"})
        self.assertNotIn("RenamedClass", self.ws.data()["sumo_nodes"])
        archive = zipfile.ZipFile(io.BytesIO(self.ws.export()))
        self.assertEqual(archive.read("sumo-changes.patch"), b"")

    def test_domain_parent_union_survives_documentation_edit(self):
        data, sources = fixture()
        sources["Domain.kif"] = "(subclass OtherBranch Hidden)\n(subclass Hidden Leaf)\n"
        ws = Workspace(Path(self.temp.name) / "domain.sqlite", data, sources)
        proposal = ws.propose({"action": "edit_doc", "class_name": "OtherBranch",
                               "doc": "Changed documentation", "initials": "TS"})
        ws.decide(proposal["id"], "apply", "TS", 0)
        graph = ws._all_parents(ws.data()["sumo_nodes"], data["sumo_nodes"])
        self.assertEqual(graph["OtherBranch"], {"Object", "Hidden"})
        with self.assertRaisesRegex(ValueError, "cycle"):
            ws.preview({"action": "move", "class_name": "Leaf",
                        "parent": "OtherBranch", "initials": "TS"})

    def test_legitimate_move_with_domain_parent_descendant(self):
        data, sources = fixture()
        sources["Domain.kif"] = "(subclass Leaf OtherBranch)\n"
        ws = Workspace(Path(self.temp.name) / "legitimate.sqlite", data, sources)
        proposal = ws.propose({"action": "move", "class_name": "Branch",
                               "parent": "OtherBranch", "initials": "TS"})
        ws.decide(proposal["id"], "apply", "TS", 0)
        graph = ws._all_parents(ws.data()["sumo_nodes"], data["sumo_nodes"])
        self.assertEqual(graph["Leaf"], {"Branch", "OtherBranch"})
        self.assertTrue(ws.export())

    def test_removed_snapshot_parent_does_not_return_after_move(self):
        self.apply({"action": "move", "class_name": "Leaf", "parent": "OtherBranch", "initials": "TS"})
        baseline = json.loads(self.ws.row()["baseline"])["sumo_nodes"]
        self.assertEqual(self.ws._all_parents(self.ws.data()["sumo_nodes"], baseline)["Leaf"], {"OtherBranch"})
        # This would falsely cycle if source Leaf -> Branch were resurrected.
        self.apply({"action": "move", "class_name": "Branch", "parent": "Leaf", "initials": "TS"})
        self.assertTrue(self.ws.export())

    def test_same_depth_move_flags_descendant_mapping_evidence(self):
        data, sources = fixture()
        for name in ("FirstParent", "SecondParent"):
            data["sumo_nodes"][name]={"label":name, "parents":["Branch"], "doc":"Parent", "origin":"upstream"}
        data["sumo_nodes"]["Leaf"]["parents"]=["FirstParent"]
        data["sumo_nodes"]["MappedChild"]={"label":"MappedChild", "parents":["Leaf"], "doc":"Child", "origin":"upstream"}
        derive(data["sumo_nodes"])
        data["links"].append({"s":"MappedChild", "l":"L2"})
        sources["Merge.kif"]=sources["Merge.kif"].replace('(subclass Leaf Branch)','(subclass Leaf FirstParent)',1)
        sources["Merge.kif"] += '(subclass FirstParent Branch)\n(subclass SecondParent Branch)\n(subclass MappedChild Leaf)\n'
        ws=Workspace(Path(self.temp.name)/"descendants.sqlite",data,sources)
        _, summary=ws.preview({"action":"move","class_name":"Leaf","parent":"SecondParent","initials":"TS"})
        self.assertEqual(summary["changed_classes"],["Leaf"])
        self.assertEqual(summary["affected_existing_classes"],["Leaf", "MappedChild"])
        self.assertEqual(summary["mapping_links_to_review"],2)

    def test_stale_proposal_rejected_without_partial_write(self):
        first = self.ws.propose(self.payload())
        second = self.ws.propose(self.payload(class_name2="unused"))
        self.ws.decide(first["id"], "apply", "TS", 0)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.ws.decide(second["id"], "apply", "TS", 1)
        self.assertEqual(self.ws.row()["revision"], 1)
        self.ws.decide(second["id"], "reject", "TS", 1)

    def test_invalid_payloads(self):
        for p in (None, [], {"action":"add"}, self.payload(doc2="unused") | {"doc":""},
                  self.payload() | {"class_name":"bad name"}, self.payload() | {"initials":3},
                  self.payload() | {"extra_parents":[{}]}):
            with self.assertRaises(ValueError):
                self.ws.propose(p)
        self.assertEqual(self.ws.edits(), [])

    def test_http_api_and_served_payload(self):
        html, _ = load_artifact(artifact())
        handler = make_handler(self.ws, html, "test-token")
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            def post(path, body, token="test-token"):
                request = urllib.request.Request(base+path, json.dumps(body).encode(),
                    {"Content-Type":"application/json", "X-OntoloMerge-Token":token})
                with urllib.request.urlopen(request) as r:
                    return json.load(r)
            with self.assertRaises(urllib.error.HTTPError) as error:
                post("/api/propose_class_edit", self.payload(), "wrong")
            self.assertEqual(error.exception.code, 403)
            result = post("/api/propose_class_edit", self.payload())
            self.assertEqual(result["status"], "provisional")
            with urllib.request.urlopen(base) as r:
                page = r.read().decode()
            self.assertIn('SUMO editor UI', page)
            self.assertNotIn('"NewClass":', page)
        finally:
            server.shutdown(); server.server_close(); thread.join()

    def test_kif_strings_comments_and_balance(self):
        parents, refs = source_index({"test.kif": '; (subclass Fake Wrong)\n(documentation Real EnglishLanguage "foo; (subclass Fake Wrong)")\n(subclass Real Entity)'})
        self.assertEqual(parents, {"Real":{"Entity"}})
        self.assertNotIn("Fake", refs)
        with self.assertRaises(ValueError):
            list(forms('(subclass Real Entity'))


class RealSnapshotTests(unittest.TestCase):
    def test_real_domain_cycle_refused_in_preview_and_export(self):
        _, data = load_artifact(artifact())
        # modsource: ontolomerge_v04_public_20261105
        # Deliberately hide this domain edge so the out-of-view cycle test
        # retains its meaning even when the selected release includes all files.
        data['sumo_nodes']['AstronomicalBody']['parents'] = [
            p for p in data['sumo_nodes']['AstronomicalBody']['parents']
            if p != 'SelfConnectedObject']
        sources = {p.name: p.read_bytes().decode("utf-8") for p in (HERE.parent / "sumo_src").glob("*.kif")}
        with tempfile.TemporaryDirectory() as temp:
            ws = Workspace(Path(temp) / "cycle.sqlite", data, sources)
            self.assertIn("SelfConnectedObject", ws.source_parents["AstronomicalBody"])
            self.assertNotIn("SelfConnectedObject", data["sumo_nodes"]["AstronomicalBody"]["parents"])
            with self.assertRaisesRegex(ValueError, "cycle"):
                ws.preview({"action": "move", "class_name": "SelfConnectedObject",
                            "parent": "AstronomicalBody", "initials": "TS"})
            # Simulate a workspace saved by the old defective editor; export
            # must independently refuse it without relying on preview history.
            current = ws.data()
            node = current["sumo_nodes"]["SelfConnectedObject"]
            node["parents"] = sorted((set(node["parents"]) - {node["sp_parent"]}) | {"AstronomicalBody"})
            con = ws.connect()
            try:
                with con:  # commits; does NOT close (sqlite3 context-manager semantics)
                    con.execute("UPDATE state SET current=? WHERE id=1", (json.dumps(current),))
            finally:
                con.close()  # Public release implementation.
            with self.assertRaisesRegex(ValueError, "KIF export refused.*cycle"):
                ws.export()

    def test_real_snapshot_preview_and_patch(self):
        html, data = load_artifact(artifact())
        sources = {p.name:p.read_bytes().decode("utf-8") for p in (HERE.parent / "sumo_src").glob("*.kif")}
        db = DB
        before = hashlib.sha256(db.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            ws = Workspace(Path(temp)/"real.sqlite", data, sources)
            payload={"action":"edit_doc", "class_name":"Entity", "doc":data["sumo_nodes"]["Entity"]["doc"] + " Test extension.", "initials":"TST"}
            projected, summary = ws.preview(payload)
            (HERE / "editor_real_preview.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
            self.assertEqual(summary["changed_classes"], ["Entity"])
            _, added = ws.preview({"action":"add", "class_name":"OntoloMergeTestClass", "parent":"IntentionalProcess", "doc":"Local fixture.", "initials":"TST"})
            self.assertEqual(added["changed_classes"], ["OntoloMergeTestClass"])
            result=ws.propose(payload)
            ws.decide(result["id"], "apply", "TST", 0)
            archive=zipfile.ZipFile(io.BytesIO(ws.export()))
            self.assertEqual(json.loads(archive.read("audit.json"))["round_trip_subclass_sets"], "PASS")
            # Prove the patch applies to the byte-exact CRLF Windows checkout.
            patch_dir=Path(temp)/"patch_check"
            patch_dir.mkdir()
            for member in archive.namelist():
                if member.startswith("edited-kif/"):
                    name=member.split("/",1)[1]
                    if name in sources:
                        (patch_dir/name).write_bytes(sources[name].encode("utf-8"))
            patch_path=Path(temp)/"changes.patch"
            patch_path.write_bytes(archive.read("sumo-changes.patch"))
            check=subprocess.run(["git","apply","--check",str(patch_path)],cwd=patch_dir,capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stdout+check.stderr)
            # Save a served page for permanent renderer boot checks.
            from serve_sumo_editor import make_handler
            new_payload=json.dumps(ws.data(),ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
            import re
            rendered=re.sub(r"const DATA = .*;(?=\s*\n)",lambda _:"const DATA = "+new_payload+";",html,count=1)
            (HERE / "editor_test_snapshot.html").write_text(rendered,encoding="utf-8")
            if "--browser" in sys.argv:
                server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(ws,html,"browser-fixture-token"))
                thread=threading.Thread(target=server.serve_forever,daemon=True)
                thread.start()
                try:
                    check=subprocess.run(["node",str(HERE / "test_sumo_editor_browser.mjs"),
                        f"--base=http://127.0.0.1:{server.server_port}","--write-test"],
                        capture_output=True,text=True,timeout=90)
                    self.assertEqual(check.returncode,0,check.stdout+check.stderr)
                finally:
                    server.shutdown(); server.server_close(); thread.join()
        self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    stream = io.StringIO()
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report=stream.getvalue()
    (HERE / "editor_test_results.txt").write_text("modsource: ontolomerge_sumo_editor_v1_20261103\n"+report,encoding="utf-8")
    print(report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
