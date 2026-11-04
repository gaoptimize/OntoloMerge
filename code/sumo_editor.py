"""sumo_editor.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import io
import json
import re
import sqlite3
import threading
import zipfile
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

MODSOURCE = "ontolomerge_sumo_editor_v1_20261103"
NAME = re.compile(r"[A-Z][A-Za-z0-9_]*\Z")
INITIALS = re.compile(r"[A-Za-z]{2,4}\Z")
ACTIONS = {"add", "edit_doc", "move", "delete", "rename"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def forms(text):
    """Top-level KIF forms and offsets; strings/comments cannot become axioms."""
    depth, start, quoted, escaped, comment = 0, 0, False, False, False
    for i, ch in enumerate(text):
        if comment:
            if ch == "\n":
                comment = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
            continue
        if ch == ";":
            comment = True
        elif ch == '"':
            quoted = True
        elif ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced KIF close parenthesis")
            if depth == 0:
                yield start, i + 1, text[start:i + 1]
    if depth or quoted:
        raise ValueError("unbalanced KIF form/string")


def tokens(form):
    # Strings remain single tokens, comments disappear. Use for symbol references.
    return re.findall(r'"(?:\\.|[^"\\])*"|[^\s();]+',
                      re.sub(r';[^\n]*(?=\n|$)', '', _hide_strings(form)[0]))


def _hide_strings(text):
    strings = []
    def hide(m):
        strings.append(m.group())
        return '""'
    return re.sub(r'"(?:\\.|[^"\\])*"', hide, text), strings


def signature(form):
    return tokens(form)


def kif_string(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


def source_index(sources):
    parents, refs = defaultdict(set), defaultdict(int)
    for text in sources.values():
        for _, _, form in forms(text):
            ts = signature(form)
            if len(ts) == 3 and ts[0] == "subclass":
                parents[ts[1]].add(ts[2])
            for symbol in set(t for t in ts if not t.startswith('"')):
                refs[symbol] += 1
    return dict(parents), dict(refs)


def check_parent_cycles(graph, terms, message):
    """Reject cycles through edited classes, allowing unrelated upstream cycles."""
    for name in terms:
        stack, seen = list(graph.get(name, [])), set()
        while stack:
            term = stack.pop()
            if term == name:
                raise ValueError(message)
            if term not in seen:
                seen.add(term)
                stack.extend(graph.get(term, []))


def derive(nodes, external=None):
    """Shortest depths across ALL parents, depth-3 branch tags, stable tree tie."""
    graph = {t: set(ps) for t, ps in (external or {}).items()}
    graph.update({t: set(n.get("parents", [])) for t, n in nodes.items()})
    children = defaultdict(list)
    for term, parents in graph.items():
        for parent in parents:
            children[parent].append(term)
    depths, queue = {"Entity": 0}, deque(["Entity"])
    while queue:
        parent = queue.popleft()
        for child in sorted(children[parent]):
            if child not in depths:
                depths[child] = depths[parent] + 1
                queue.append(child)
    if nodes.keys() - depths.keys():
        raise ValueError("edit would leave classes unreachable from Entity")
    for term in sorted(nodes, key=lambda t: (depths[t], t)):
        node = nodes[term]
        node["depth"] = depths[term]
        shortest = sorted(p for p in node.get("parents", [])
                          if p in nodes and depths.get(p, -2) + 1 == depths[term])
        if term != "Entity" and not shortest:
            raise ValueError(f"{term}: shortest parent is outside mapped snapshot; expand the snapshot before editing this branch")
        # Preserve existing tree tie where still shortest; otherwise lexical tie.
        node["sp_parent"] = (node.get("sp_parent") if node.get("sp_parent") in shortest
                             else shortest[0] if shortest else None)
    # Matches freeze_sumo_levels.py: depth-3 anchors on shortest paths only.
    cache = {}
    def branches(term, visiting):
        if term in cache:
            return cache[term]
        if term in visiting:
            raise ValueError("edit would create a cycle")
        visiting = visiting | {term}
        result = {term} if depths[term] == 3 else set()
        for parent in graph.get(term, []):
            if depths.get(parent) != depths[term] - 1:
                continue
            result |= branches(parent, visiting)
        cache[term] = result
        return result
    for term in nodes:
        nodes[term]["branches"] = sorted(branches(term, set()))


class Workspace:
    def __init__(self, path, baseline, sources):
        self.path = Path(path)
        self.lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS state (
              id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL,
              baseline TEXT NOT NULL, current TEXT NOT NULL, sources TEXT NOT NULL,
              source_hash TEXT NOT NULL, modsource TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS class_edit (
              id INTEGER PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL,
              base_revision INTEGER NOT NULL, created_utc TEXT NOT NULL,
              decided_utc TEXT, decided_by TEXT, before_state TEXT, after_state TEXT,
              modsource TEXT NOT NULL);
            """)
            if not con.execute("SELECT 1 FROM state").fetchone():
                data = copy.deepcopy(baseline)
                for node in data["sumo_nodes"].values():
                    node["origin"] = "upstream"
                # Validate, but retain the published depths/tags until first apply.
                derive(copy.deepcopy(data["sumo_nodes"]), source_index(
                    {"Merge.kif": sources["Merge.kif"]} if "Merge.kif" in sources else sources)[0])
                digest = hashlib.sha256(encoded(sources).encode()).hexdigest()
                con.execute("INSERT INTO state VALUES(1,0,?,?,?,?,?)",
                            (encoded(data), encoded(data), encoded(sources), digest, MODSOURCE))
        self.sources = json.loads(self.row()["sources"])
        self.source_parents, self.references = source_index(self.sources)
        self.depth_parents = source_index({"Merge.kif": self.sources["Merge.kif"]}
                                         if "Merge.kif" in self.sources else self.sources)[0]

    def connect(self):
        con = sqlite3.connect(str(self.path), timeout=30)
        con.row_factory = sqlite3.Row
        return con

    def row(self):
        with self.connect() as con:
            return dict(con.execute("SELECT * FROM state WHERE id=1").fetchone())

    def edits(self):
        with self.connect() as con:
            return [dict(r, payload=json.loads(r["payload"])) for r in con.execute(
                "SELECT id,payload,status,base_revision,created_utc,decided_utc,decided_by "
                "FROM class_edit ORDER BY id DESC")]

    def data(self):
        row = self.row()
        data = json.loads(row["current"])
        data["editor"] = {"revision": row["revision"], "modsource": MODSOURCE,
                          "applied": sum(e["status"] == "applied" for e in self.edits())}
        return data

    def _all_parents(self, nodes, baseline):
        graph = {t: set(ps) for t, ps in self.source_parents.items()}
        for t in baseline.keys() - nodes.keys():
            graph.pop(t, None)
        for t, n in nodes.items():
            parents = set(n.get("parents", []))
            # Only parent edits replace source assertions. Documentation/derived
            # changes must preserve domain-file and snapshot-only ancestry.
            if t in baseline and parents == set(baseline[t].get("parents", [])):
                graph.setdefault(t, set()).update(parents)
            else:
                graph[t] = parents
        return graph

    def preview(self, payload, current=None, baseline=None):
        if not isinstance(payload, dict):
            raise ValueError("expected a JSON object")
        if current is None:
            row = self.row()
            current, baseline = json.loads(row["current"]), json.loads(row["baseline"])
        data = copy.deepcopy(current)
        nodes, original = data["sumo_nodes"], baseline["sumo_nodes"]
        action, name = payload.get("action"), payload.get("class_name")
        if action not in ACTIONS:
            raise ValueError("choose add, edit_doc, move, delete or rename")
        if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 120:
            raise ValueError("class name must start with a capital and contain letters, digits or underscores")
        if not isinstance(payload.get("initials"), str) or not INITIALS.fullmatch(payload["initials"]):
            raise ValueError("initials must be 2–4 letters")
        if not isinstance(payload.get("note", ""), str) or len(payload.get("note", "")) > 4000:
            raise ValueError("note must be text, at most 4000 characters")
        if action != "add" and name not in nodes:
            raise ValueError(f"unknown class {name}")
        if name == "Entity" and action not in {"edit_doc"}:
            raise ValueError("Entity is the root and cannot be moved, renamed or deleted")
        before = copy.deepcopy(nodes.get(name))
        if action == "add":
            if name in nodes or name in self.references or name in self.source_parents:
                raise ValueError(f"{name} already exists in the workspace or vendored KIF")
            nodes[name] = {"label": name, "origin": "local", "parents": [], "doc": ""}
        if action in {"add", "edit_doc"}:
            doc = payload.get("doc")
            if not isinstance(doc, str) or not doc.strip() or len(doc) > 30000 or "\x00" in doc:
                raise ValueError("documentation is required (maximum 30000 characters)")
            nodes[name]["doc"] = doc.strip()
        if action in {"add", "move"}:
            parent = payload.get("parent")
            if not isinstance(parent, str) or parent not in nodes or parent == name:
                raise ValueError("choose a different, existing target parent")
            if action == "add":
                extra = payload.get("extra_parents", [])
                if not isinstance(extra, list) or any(not isinstance(p, str) or p not in nodes or p == name for p in extra):
                    raise ValueError("secondary parents must be existing classes")
                nodes[name]["parents"] = sorted(set([parent] + extra))
            else:
                old = nodes[name].get("sp_parent")
                if not old or old == parent:
                    raise ValueError("target must differ from the current displayed parent")
                if parent in nodes[name]["parents"]:
                    raise ValueError("target is already a secondary parent; use a different target")
                nodes[name]["parents"] = sorted((set(nodes[name]["parents"]) - {old}) | {parent})
            nodes[name]["sp_parent"] = parent
            graph = self._all_parents(nodes, original)
            check_parent_cycles(graph, [name],
                                "move/add would create a cycle (checked through secondary and out-of-view parents)")
        if action in {"delete", "rename"}:
            graph = self._all_parents(nodes, original)
            children = sorted(t for t, ps in graph.items() if name in ps)
            links = sum(l["s"] == name for l in data["links"])
            # Upstream classes can occur in arbitrary rules, domains, disjointness,
            # instances, termFormat etc. A tree editor must not silently rewrite them.
            if nodes[name].get("origin") != "local":
                raise ValueError(f"upstream {action} needs a full axiom audit: {len(children)} subclass children, "
                                 f"{links} mapped links, {self.references.get(name, 0)} KIF forms reference {name}. "
                                 "This release restricts delete/rename to local classes.")
            if children or links:
                raise ValueError(f"cannot {action}: {len(children)} subclass children, {links} mapped links")
            if action == "delete":
                del nodes[name]
            else:
                new = payload.get("new_name")
                if not isinstance(new, str) or not NAME.fullmatch(new) or len(new) > 120:
                    raise ValueError("new name must be a valid capitalized class name")
                if new in nodes or new in self.references:
                    raise ValueError("new name already exists in workspace or KIF")
                nodes[new] = nodes.pop(name)
                nodes[new]["label"] = new
        if action != "edit_doc":
            # The mapping's published taxonomy is Merge.kif, not a union of all
            # domain ontologies. Preserve that scope for depths/branch anchors.
            depth_graph = {t: set(ps) for t, ps in self.depth_parents.items()}
            depth_graph.update({t: set(n.get("parents", [])) for t, n in nodes.items()})
            derive(nodes, depth_graph)
        changed = sorted(t for t in nodes if t not in current["sumo_nodes"] or
                         nodes[t] != current["sumo_nodes"][t])
        removed = sorted(current["sumo_nodes"].keys() - nodes.keys())
        affected = set(t for t in changed + removed if t in original)
        if action == "move":
            # Same-depth reparenting can change descendant semantics without
            # changing any cached depth/tag. Include the entire DAG subtree.
            graph = self._all_parents(nodes, original)
            children = defaultdict(set)
            for term, parents in graph.items():
                for parent in parents:
                    children[parent].add(term)
            stack, seen = [name], set()
            while stack:
                term = stack.pop()
                if term not in seen:
                    seen.add(term)
                    stack.extend(children[term])
            affected |= seen & original.keys()
        stale = set(data.get("editor_stale_terms", [])) | affected
        data["editor_stale_terms"] = sorted(stale)
        # Rebuild branch selector from the current tree. Frozen mapping evidence
        # remains visible, explicitly marked as requiring review after tree edits.
        stats = defaultdict(lambda: {"sumo": 0, "links": 0, "lcc": set(), "holes": 0})
        for term, n in nodes.items():
            for branch in n["branches"]:
                stats[branch]["sumo"] += 1
                for lk in data["links"]:
                    if lk["s"] == term:
                        stats[branch]["links"] += 1
                        stats[branch]["lcc"].add(lk["l"])
        data["branches"] = [dict(name=b, **{**v, "lcc": len(v["lcc"])})
                            for b, v in sorted(stats.items(), key=lambda kv: (-kv[1]["links"], kv[0]))]
        summary = {"modsource": MODSOURCE, "action": action, "class_name": name, "before": before,
                   "after": nodes.get(payload.get("new_name") if action == "rename" else name),
                   "changed_classes": changed, "removed_classes": removed,
                   "affected_existing_classes": sorted(affected),
                   "mapping_links_to_review": sum(lk["s"] in affected for lk in data["links"]),
                   "warning": "Mapped links and hole evidence remain frozen; affected classes require reconciliation." if affected else "Local class; no published mapping is changed."}
        if data["sumo_nodes"] == current["sumo_nodes"]:
            raise ValueError("this proposal makes no change")
        return data, summary

    def propose(self, payload):
        with self.lock, self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = dict(con.execute("SELECT * FROM state").fetchone())
            _, summary = self.preview(payload, json.loads(row["current"]), json.loads(row["baseline"]))
            cur = con.execute("INSERT INTO class_edit(payload,status,base_revision,created_utc,modsource) "
                              "VALUES(?,'provisional',?,?,?)",
                              (encoded(payload), row["revision"], now(), MODSOURCE))
            return {"id": cur.lastrowid, "summary": summary, "status": "provisional"}

    def decide(self, edit_id, decision, initials, revision):
        if not isinstance(initials, str) or not INITIALS.fullmatch(initials):
            raise ValueError("reviewer initials must be 2–4 letters")
        if decision not in {"apply", "reject"}:
            raise ValueError("decision must be apply or reject")
        with self.lock, self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = dict(con.execute("SELECT * FROM state").fetchone())
            edit = con.execute("SELECT * FROM class_edit WHERE id=?", (edit_id,)).fetchone()
            if not edit or edit["status"] != "provisional":
                raise ValueError("proposal no longer pending")
            if revision != row["revision"]:
                raise ValueError("workspace changed; refresh and preview again")
            if decision == "apply" and edit["base_revision"] != row["revision"]:
                raise ValueError("proposal is stale; reject and re-propose against the current tree")
            if decision == "apply":
                data, summary = self.preview(json.loads(edit["payload"]), json.loads(row["current"]), json.loads(row["baseline"]))
                # Backup the committed pre-apply state using a separate reader.
                backup_dir = self.path.parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup = backup_dir / f"before_edit_{edit_id}_rev_{row['revision']}.sqlite"
                if not backup.exists():
                    with self.connect() as reader, sqlite3.connect(str(backup)) as dest:
                        reader.backup(dest)
                con.execute("UPDATE state SET current=?, revision=revision+1,modsource=? WHERE id=1",
                            (encoded(data), MODSOURCE))
                con.execute("UPDATE class_edit SET before_state=?,after_state=? WHERE id=?",
                            (row["current"], encoded(data), edit_id))
            else:
                summary = None
            con.execute("UPDATE class_edit SET status=?,decided_by=?,decided_utc=?,modsource=? WHERE id=?",
                        ("applied" if decision == "apply" else "rejected", initials.upper(), now(), MODSOURCE, edit_id))
            return {"ok": True, "summary": summary, "revision": row["revision"] + (decision == "apply")}

    def export(self):
        """Real unified source diffs, edited KIF, audit log; never edit vendored KIF."""
        with self.lock:
            row = self.row()
            baseline = json.loads(row["baseline"])["sumo_nodes"]
            current = json.loads(row["current"])["sumo_nodes"]
            sources = self.sources
            transformed = {}
            edge_remove, doc_replace = set(), {}
            additions = []
            for name in baseline.keys() & current.keys():
                old, new = baseline[name], current[name]
                edge_remove |= {(name, p) for p in set(old.get("parents", [])) - set(new.get("parents", []))}
                additions.extend(f"(subclass {name} {p})" for p in sorted(set(new.get("parents", [])) - set(old.get("parents", []))))
                if old.get("doc", "") != new.get("doc", ""):
                    doc_replace[name] = new["doc"]
            for name in sorted(current.keys() - baseline.keys()):
                additions.extend(f"(subclass {name} {p})" for p in current[name]["parents"])
                additions.append(f"(documentation {name} EnglishLanguage {kif_string(current[name]['doc'])})")
            found_edges, found_docs = set(), set()
            for filename, text in sources.items():
                replacements = []
                newline = "\r\n" if "\r\n" in text else "\n"
                for start, end, form in forms(text):
                    ts = signature(form)
                    if len(ts) == 3 and ts[0] == "subclass" and tuple(ts[1:]) in edge_remove:
                        found_edges.add(tuple(ts[1:]))
                        replacements.append((start, end, f"; {MODSOURCE}: removed subclass {ts[1]} {ts[2]}{newline}"))
                    if len(ts) == 4 and ts[:1] == ["documentation"] and ts[1] in doc_replace and ts[2] in {"EnglishLanguage", "EnglishWrittenLanguage"}:
                        found_docs.add(ts[1])
                        document = kif_string(doc_replace[ts[1]]).replace("\r\n", "\n").replace("\n", newline)
                        replacements.append((start, end, f"(documentation {ts[1]} {ts[2]} {document})"))
                for start, end, replacement in reversed(replacements):
                    text = text[:start] + replacement + text[end:]
                transformed[filename] = text
            if edge_remove - found_edges:
                raise ValueError(f"KIF export refused: removed edges absent in vendored sources: {sorted(edge_remove - found_edges)}")
            for name in sorted(doc_replace.keys() - found_docs):
                additions.append(f"(documentation {name} EnglishLanguage {kif_string(doc_replace[name])})")
            if additions:
                transformed["OntoloMerge-local.kif"] = sources.get("OntoloMerge-local.kif", "") + f"\n; modsource: {MODSOURCE}\n; Local workspace delta. Review before upstream submission.\n" + "\n\n".join(additions) + "\n"
            # Round trip ALL top-level subclass assertions, including out-of-view
            # nodes, so removal comments cannot masquerade as removed assertions.
            actual, _ = source_index(transformed)
            expected = {t: set(ps) for t, ps in self.source_parents.items()}
            for child, parent in edge_remove:
                expected.setdefault(child, set()).discard(parent)
            for term, n in current.items():
                if term not in baseline:
                    expected[term] = set(n["parents"])
                else:
                    for p in set(n["parents"]) - set(baseline[term].get("parents", [])):
                        expected.setdefault(term, set()).add(p)
            if {t: ps for t, ps in actual.items() if ps} != {t: ps for t, ps in expected.items() if ps}:
                raise ValueError("KIF subclass round-trip equality failed")
            # Check snapshot-only ancestry as well as every assertion actually
            # retained in the exported domain files, even for edited classes.
            graph = self._all_parents(current, baseline)
            for term, parents in actual.items():
                graph.setdefault(term, set()).update(parents)
            edited_parents = [t for t, n in current.items() if t not in baseline or
                              set(n.get("parents", [])) != set(baseline[t].get("parents", []))]
            check_parent_cycles(graph, edited_parents,
                                "KIF export refused: edit would create a cycle (including assertions outside the visible map)")
            diff = []
            for filename in sorted(transformed):
                before, after = sources.get(filename, ""), transformed[filename]
                if before != after:
                    diff.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                   fromfile=f"a/{filename}" if filename in sources else "/dev/null",
                                                   tofile=f"b/{filename}"))
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("sumo-changes.patch", "".join(diff))
                for filename, text in transformed.items():
                    if text != sources.get(filename, ""):
                        archive.writestr("edited-kif/" + filename, text)
                archive.writestr("audit.json", encoded({"modsource": MODSOURCE, "revision": row["revision"],
                    "source_hashes": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sources.items()},
                    "edits": self.edits(), "round_trip_subclass_sets": "PASS",
                    "mapping_reconciliation": "not performed; affected mapping evidence remains frozen"}))
                archive.writestr("README.txt", "OntoloMerge SUMO workspace export\n"
                    "modsource: " + MODSOURCE + "\n"
                    "Apply sumo-changes.patch to the matching upstream snapshot; edited-kif contains complete changed files.\n"
                    "Do not append this patch to SUMO. The diff removes as well as adds assertions.\n"
                    "Top-level subclass sets were round-trip checked, including out-of-view classes.\n"
                    "This is structural verification, not theorem proving or SUMO maintainer approval.\n"
                    "The published mapping database and vendored KIF were never modified.\n")
            return buffer.getvalue()
