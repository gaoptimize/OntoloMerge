#!/usr/bin/env python3
"""extract_lcc_notes.py — OntoloMerge public release.
Requirements: pypdf (only for re-extracting LC notes).
modsource: ontolomerge_github_path_guard_20261103
"""

import csv
import re
import sys
from pathlib import Path

from pypdf import PdfReader  # noqa: E402

HERE = Path(__file__).resolve().parent
LCC_MAP = HERE.parent
PDF_DIR = LCC_MAP / "inputs" / "lccs_pdf"
OUTLINE = LCC_MAP / "inputs" / "lcc_outline_20261102.tsv"
OUT = LCC_MAP / "inputs" / "lcc_notes_20261102.tsv"

MODSOURCE = "ontolomerge_lccnotes_v0_1_20261102"

HEADER = re.compile(r"^([A-Z]{1,3})\b.*\b\1\s*$")
ENTRY = re.compile(
    r"^\s*(\(?\d[\d.]*(?:\.[A-Z][A-Za-z0-9.\-]*)?(?:-[\d.]+)?\)?)"
    r"\s{1,4}(.*\S)\s*$")
NOTE = re.compile(r"^\s*(Cf\.|Including|Class here|For\b.*\bsee\b|see)\s*(.*)$",
                  re.IGNORECASE)
TABLE_START = re.compile(r"^\s*(Table for|Apply Table|TABLE)\b")
PAGENO = re.compile(r"^\s*\d{1,4}\s*$")


def parse_mark(mark):
    """'8053.5' -> 8053.5 ; '(6128)' -> 6128.0 ; '6133.A-.W' -> 6133.0"""
    s = mark.strip("()").split("-")[0]
    m = re.match(r"^(\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else None


def parse_schedule(pdf_path):
    """Yield entries: dict(num|None, mark, caption, notes=[(kind, text)],
    subclass)."""
    entries = []
    r = PdfReader(str(pdf_path))
    subclass = None
    cur = None
    in_table = False
    for page in r.pages:
        text = page.extract_text() or ""
        lines = text.split("\n")
        # running header: second line looks like 'HG FINANCE HG'
        if len(lines) > 1:
            h = HEADER.match(lines[1].strip())
            if h:
                subclass = h.group(1)
                in_table = False
        for line in lines:
            if PAGENO.match(line):
                continue
            m = ENTRY.match(line)
            n = NOTE.match(line)
            if TABLE_START.match(line):
                in_table = True
            if m and not n:
                num = parse_mark(m.group(1))
                # inside tables, small numbers are local table rows: skip
                if in_table and num is not None and num < 50:
                    continue
                cur = {"num": num, "mark": m.group(1),
                       "caption": m.group(2).strip(), "notes": [],
                       "subclass": subclass}
                entries.append(cur)
                # a real entry with a normal number ends the table block
                if num is not None and num >= 50:
                    in_table = False
            elif n and cur is not None:
                cur["notes"].append((n.group(1), n.group(2).strip()))
            elif (cur is not None and cur["notes"]
                    and line.startswith("                ") and line.strip()):
                k, v = cur["notes"][-1]
                cur["notes"][-1] = (k, v + " " + line.strip())
            elif (cur is not None and not cur["notes"]
                    and line.startswith("      ") and line.strip()
                    and not line.strip().endswith(".")
                    and len(line.strip().split()) < 10
                    and "--" not in line):
                # caption continuation line
                cur["caption"] += " " + line.strip()
    return entries


def parse_code(code):
    """'HG8011-9999' -> ('HG', 8011.0, 9999.0); 'D383' -> ('D', 383.0, 383.0)"""
    m = re.match(r"^([A-Z]{1,3})(\d[\d.]*)?(?:-(\d[\d.]*)?)?$", code)
    if not m:
        return None
    sub = m.group(1)
    try:
        a = float(m.group(2)) if m.group(2) else None
        b = float(m.group(3)) if m.group(3) else a
    except ValueError:
        return None
    return sub, a, b


def main():
    rows = []
    with open(OUTLINE, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            p = parse_code(row["code"])
            if p and p[1] is not None:
                sub, a, b = p
                rows.append({"row_id": row["row_id"], "sub": sub,
                             "a": a, "b": b, "span": b - a})
    print(f"outline rows with numeric codes: {len(rows)}")

    by_sub = {}
    for r in rows:
        by_sub.setdefault(r["sub"], []).append(r)
    for v in by_sub.values():
        v.sort(key=lambda r: r["span"])

    out_rows = []
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    print(f"schedule PDFs: {len(pdfs)}")
    for pdf in pdfs:
        entries = parse_schedule(pdf)
        n_entries = n_notes = n_attached = 0
        for e in entries:
            n_entries += 1
            if e["num"] is None or not e["notes"]:
                continue
            sub_rows = by_sub.get(e["subclass"] or "", [])
            hit = None
            for r in sub_rows:  # sorted by span: most specific first
                if r["a"] - 1e-9 <= e["num"] <= r["b"] + 1e-9:
                    hit = r
                    break
            if not hit:
                continue
            for kind, text in e["notes"]:
                n_notes += 1
                out_rows.append([hit["row_id"], kind, text,
                                 e["mark"], e["caption"], pdf.stem])
                n_attached += 1
        print(f"  {pdf.stem:14s} entries {n_entries:6d} "
              f"notes-attached {n_attached:5d}")

    # dedupe identical notes on the same row
    seen = set()
    dedup = []
    for r in out_rows:
        key = (r[0], r[1], r[2])
        if key not in seen:
            seen.add(key)
            dedup.append(r)

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["row_id", "kind", "text", "src_mark", "src_caption",
                    "schedule", "modsource"])
        for r in dedup:
            w.writerow(r + [MODSOURCE])
    print(f"wrote {OUT}: {len(dedup)} note rows "
          f"(deduped from {len(out_rows)})")


if __name__ == "__main__":
    main()
