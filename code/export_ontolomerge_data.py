#!/usr/bin/env python3
"""export_ontolomerge_data.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""

import argparse
import csv
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LCC_MAP = HERE.parent


def _pick(primary, *alts):
    """First existing path wins; keeps the repo layout working while letting
    the packaged layout (data/…) drive the same script."""
    for p in (primary, *alts):
        if p.exists():
            return p
    return primary


DB = _pick(LCC_MAP / "sumo_lcc_map.sqlite",
           LCC_MAP / "data" / "ontolomerge_public.sqlite")
SUMO_LEVELS = _pick(LCC_MAP / "inputs" / "sumo_levels_20261102.tsv",
                    LCC_MAP / "data" / "sumo_levels_20261102.tsv")
RELABEL_PLAN = LCC_MAP / "reconcile" / "containment" / "d5_relabel_plan.tsv"
RERANK_TOP5 = LCC_MAP / "reconcile" / "containment" / "rerank_top5.tsv"
DIRTY_BASTARDS = LCC_MAP / "reconcile" / "containment" / "dirty_bastards.tsv"
LCC_NOTES = _pick(LCC_MAP / "inputs" / "lcc_notes_merged_20261102.tsv",
                  LCC_MAP / "data" / "lcc_notes_merged_20261102.tsv",
                  LCC_MAP / "inputs" / "lcc_notes_20261102.tsv",
                  LCC_MAP / "data" / "lcc_notes_20261102.tsv")
TEMPLATE = HERE / "ontolomerge.html"

MODSOURCE = "ontolomerge_github_editor_v0_3_20261103"
PUBLIC = False  # Public release implementation.


def ro_connect():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def load_sumo_branches():
    """term -> (depth, [branch tokens]) from the frozen tree."""
    out = {}
    with open(SUMO_LEVELS, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["term"]] = (int(r["depth"]), r["branch"].split())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--public", action="store_true",
                    help="patent scrub: drop per-seat fields (link seats,"
                         " contested verdicts) for public release")
    ap.add_argument("--out", default=None,
                    help="output path (default: HERE/ontolomerge_v0_1_<date>.html)")
    args = ap.parse_args()
    global PUBLIC
    PUBLIC = args.public

    con = ro_connect()

    # --- SUMO nodes -----------------------------------------------------
    sumo_nodes = {}
    for nid, label, depth, doc in con.execute(
        "SELECT node_id, label, depth, doc FROM node WHERE scheme='SUMO'"
    ):
        sumo_nodes[nid] = {"label": label, "depth": depth, "doc": doc or ""}

    # SUMO parent structure: shortest-path parent plus all parents (DAG).
    sp_parent, all_parents = {}, defaultdict(list)
    for child, parent, osp in con.execute(
        "SELECT child, parent, on_shortest_path FROM edge WHERE scheme='SUMO'"
    ):
        all_parents[child].append(parent)
        if osp:
            sp_parent[child] = parent
    for nid in sumo_nodes:
        sumo_nodes[nid]["sp_parent"] = sp_parent.get(nid)
        sumo_nodes[nid]["parents"] = sorted(all_parents.get(nid, []))

    branches_of = load_sumo_branches()
    for nid, (depth, toks) in branches_of.items():
        if nid in sumo_nodes:
            sumo_nodes[nid]["branches"] = toks

    # --- LCC nodes ------------------------------------------------------
    lcc_nodes = {}
    for nid, code, label, depth in con.execute(
        "SELECT node_id, code, label, depth FROM node WHERE scheme='LCC'"
    ):
        lcc_nodes[nid] = {"code": code, "label": label, "depth": depth}
    lcc_parent = {}
    for child, parent in con.execute(
        "SELECT child, parent FROM edge WHERE scheme='LCC' AND on_shortest_path=1"
    ):
        lcc_parent[child] = parent
    for nid in lcc_nodes:
        lcc_nodes[nid]["parent"] = lcc_parent.get(nid)

    # --- Links ----------------------------------------------------------
    # the public (scrubbed) sqlite has no per-seat `seats` column
    fl_cols = {r[1] for r in con.execute("PRAGMA table_info(final_link)")}
    seats_expr = "seats" if "seats" in fl_cols else "NULL"
    links = []
    for s, l, rel, status, direc, n, seats in con.execute(
        "SELECT sumo_term, lcc_row_id, final_relation, status, directions,"
        f" n_seats, {seats_expr} FROM final_link"
    ):
        links.append({
            "s": s, "l": l, "rel": rel, "status": status,
            "dir": direc, "n": n, "seats": seats,
        })

    # Public release implementation.
    holes = []
    for branch, direc, s, l, why in con.execute(
        "SELECT branch, direction, sumo_term, lcc_row_id, why FROM merged_hole"
    ):
        holes.append({"branch": branch, "dir": direc, "s": s, "l": l, "why": why})

    # --- Contested overlay: the strict-containment relabel plan ----------
    # Public release implementation.
    # RELABEL_RELATED, KEEP_BROADER with a basis column; meaning moves from
    # "disputed" to "planned relabel". Show ONLY rows where the plan still
    # Public release implementation.
    # the DB, the overlay self-clears and final_relation is authoritative.
    ACTION_TARGET = {"RELABEL_PARTIAL": "partial",
                     "RELABEL_RELATED": "related",
                     "KEEP_BROADER": "broader"}
    current_rel = {f"{lk['s']}|{lk['l']}": lk["rel"] for lk in links}
    contested = {}
    if RELABEL_PLAN.exists():
        with open(RELABEL_PLAN, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                key = f"{r['sumo_term']}|{r['lcc_row_id']}"
                target = ACTION_TARGET.get(r.get("action", ""))
                if not target or current_rel.get(key) == target:
                    continue
                contested[key] = {"action": r["action"], "target": target,
                                  "basis": r.get("basis", "")}

    overlays_file = LCC_MAP / "data" / "viewer_overlays.json"
    frozen_overlays = json.loads(overlays_file.read_text(encoding="utf-8")) if overlays_file.exists() else {}
    if not RELABEL_PLAN.exists():
        contested = frozen_overlays.get("contested", {})

    if PUBLIC:
        # Public release implementation.
        # verdicts for exactly this revisit): drop per-seat fields; the
        # corroboration count (lk.n) and contested action/target stay.
        # basis text can carry editorial seat mentions — blank it too.
        for lk in links:
            lk.pop("seats", None)
        for c in contested.values():
            c["basis"] = ""

    # --- Bastard children: fall-out concepts with no LCC home ------------
    # rerank_top5.tsv suggestion=BASTARD_CHILD (59 rows, 37 distinct classes).
    # dirty_bastards.tsv holds the verified SUMO faults among them (6).
    bastards = {}
    if RERANK_TOP5.exists():
        with open(RERANK_TOP5, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r["suggestion"] == "BASTARD_CHILD":
                    bastards[r["x_sumo"]] = {
                        "counterexample": r["counterexample"],
                        "fell_from": f"{r['fell_from_row']} {r['fell_from_label']}",
                    }
    if DIRTY_BASTARDS.exists():
        with open(DIRTY_BASTARDS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                b = bastards.setdefault(r["x_sumo"], {})
                b["dirty"] = r["dirty_type"]

    if not RERANK_TOP5.exists() and not DIRTY_BASTARDS.exists():
        bastards = frozen_overlays.get("bastards", {})

    # --- LCC schedule notes (scope notes from the free full-text schedules)
    # extract_lcc_notes.py -> inputs/lcc_notes_*.tsv. Attach at most
    # NOTES_CAP per row, priority: Class here > Including > Cf. > For/see.
    NOTE_PRIORITY = {"Class": 0, "class_here": 0, "instruction": 0,
                     "Including": 1, "including": 1,
                     "Cf.": 2, "cf": 2,
                     "For": 3, "for": 3,
                     "see": 4, "See": 4, "see_ref": 4, "see_elsewhere": 4}
    NOTES_CAP = 12
    lcc_notes = defaultdict(list)
    if LCC_NOTES.exists():
        with open(LCC_NOTES, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                lcc_notes[r["row_id"]].append({"k": r["kind"], "v": r["text"]})
        for rid, ns in lcc_notes.items():
            ns.sort(key=lambda n: NOTE_PRIORITY.get(n["k"].split()[0], 5))
            total = len(ns)
            lcc_notes[rid] = {"notes": ns[:NOTES_CAP], "total": total}

    # --- Branch summary (drives the selector; recomputed, not baked) ----
    term_branches = {t: toks for t, (d, toks) in branches_of.items()}
    links_by_sumo = defaultdict(list)
    for lk in links:
        links_by_sumo[lk["s"]].append(lk)
    branch_stats = defaultdict(lambda: {"sumo": 0, "links": 0, "lcc": set(), "holes": 0})
    for term, toks in term_branches.items():
        for b in toks:
            branch_stats[b]["sumo"] += 1
            for lk in links_by_sumo.get(term, []):
                branch_stats[b]["links"] += 1
                branch_stats[b]["lcc"].add(lk["l"])
    for h in holes:
        branch_stats[h["branch"]]["holes"] += 1
    branches = [
        {"name": b, "sumo": v["sumo"], "links": v["links"],
         "lcc": len(v["lcc"]), "holes": v["holes"]}
        for b, v in sorted(branch_stats.items(),
                           key=lambda kv: -kv[1]["links"])
    ]

    data = {
        "meta": {
            "modsource": MODSOURCE,
            "generated": date.today().isoformat(),
            "public_scrub": PUBLIC,
            "counts": {
                "sumo_nodes": len(sumo_nodes), "lcc_nodes": len(lcc_nodes),
                "links": len(links), "holes": len(holes),
                "contested": len(contested),
                "link_status": dict(Counter(lk["status"] for lk in links)),
                "link_relation": dict(Counter(lk["rel"] for lk in links)),
            },
            "note": ("Relations read from final_link.final_relation at export"
                     " time. d5_relabel_plan.tsv is a PLAN (not applied);"
                     " shown as the contested overlay."),
        },
        "branches": branches,
        "sumo_nodes": sumo_nodes,
        "lcc_nodes": lcc_nodes,
        "links": links,
        "holes": holes,
        "contested": contested,
        "bastards": bastards,
        "lcc_notes": dict(lcc_notes),
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    placeholder = "/*__ONTOMERGE_DATA__*/"
    if placeholder not in html:
        sys.exit(f"template {TEMPLATE} is missing {placeholder}")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    out = (Path(args.out) if args.out
           else (LCC_MAP if (LCC_MAP / "data" / "ontolomerge_public.sqlite").exists() else HERE)
           / f"ontolomerge_v0_1_{date.today():%Y%m%d}.html")
    out.write_text(html.replace(placeholder, f"const DATA = {payload};"),
                   encoding="utf-8")

    print(f"wrote {out}")
    print(f"  payload {len(payload)/1e6:.2f} MB, "
          f"total {out.stat().st_size/1e6:.2f} MB")
    print(f"  branches: {len(branches)}, links: {len(links)}, "
          f"holes: {len(holes)}, contested: {len(contested)}, "
          f"bastards: {len(bastards)}, lcc rows with notes: {len(lcc_notes)}")
    con.close()


if __name__ == "__main__":
    main()
