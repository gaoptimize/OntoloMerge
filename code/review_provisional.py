#!/usr/bin/env python3
"""review_provisional.py — OntoloMerge public release.
modsource: ontolomerge_github_path_guard_20261103
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parent / "sumo_lcc_map.sqlite"
if not DB.exists():
    DB = HERE.parent / "data" / "ontolomerge_public.sqlite"
MODSOURCE = "ontolomerge_github_editor_v0_3_20261103"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["list", "approve", "reject"])
    ap.add_argument("ids", nargs="*", type=int)
    ap.add_argument("--initials", help="admin initials, 2-4 letters")
    ap.add_argument("--reason", default="")
    args = ap.parse_args()

    if not DB.is_file():
        sys.exit(f"mapping database not found: {DB}")
    con = sqlite3.connect(str(DB))
    con.execute("PRAGMA journal_mode=WAL")

    if args.cmd == "list":
        rows = con.execute(
            "SELECT id, action, sumo_term, lcc_row_id, relation, direction,"
            " initials, created_utc, COALESCE(note,'')"
            " FROM provisional_link WHERE status='provisional' ORDER BY id"
        ).fetchall()
        if not rows:
            print("no provisional rows")
        for r in rows:
            print(f"#{r[0]:<4} {r[1]:<7} {r[2]} <-> {r[3]}  {r[4]:<9}"
                  f" {r[5]:<3} by {r[6]} at {r[7]}"
                  + (f"  note: {r[8]}" if r[8] else ""))
        return

    if not args.ids:
        sys.exit("give at least one provisional id")
    if not args.initials or not args.initials.isalpha()\
            or not 2 <= len(args.initials) <= 4:
        sys.exit("--initials required (2-4 letters)")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new = "approved" if args.cmd == "approve" else "rejected"
    for pid in args.ids:
        cur = con.execute(
            "UPDATE provisional_link SET status=?, decided_utc=?,"
            " decided_by=? WHERE id=? AND status='provisional'",
            (new, now, args.initials.upper(), pid))
        if cur.rowcount:
            if args.reason:
                con.execute(
                    "UPDATE provisional_link SET note = note || ? WHERE id=?",
                    (f" [admin: {args.reason}]", pid))
            print(f"#{pid} -> {new} by {args.initials.upper()} at {now}")
        else:
            print(f"#{pid}: no provisional row with that id")
    con.commit()


if __name__ == "__main__":
    main()
