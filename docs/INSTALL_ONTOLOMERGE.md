# OntoloMerge — Install & Operations Manual

**Release:** Initial · viewer, mapping workbench and SUMO tree editor  
**modsource:** ontolomerge_github_path_guard_20261103

## 1. Requirements and quick start

Viewing requires only a modern browser. Open the dated HTML file directly; it is
self-contained and read-only. Both local servers require Python 3.10 or newer and
use only the standard library. There are no model calls or runtime downloads.

Only re-extracting LC notes with `code/extract_lcc_notes.py` requires `pypdf`
(`python -m pip install pypdf`). The viewer and editor do not need it.

For the **GitHub package**, extract the zip and run from its `ontolomerge` folder:

```bash
python code/serve_sumo_editor.py
# Open http://127.0.0.1:41772/
```

For the older mapping-only server:

```bash
python code/serve_ontolomerge.py
# Open http://127.0.0.1:41771/
```

Keep the terminal open; Ctrl+C stops the server. The servers bind to loopback only
and are intended for a single local user. Extract into a writable folder so the
editor can create its workspace and backups.

If your workstation uses **Python Guardian**, run these Python files through it.
The Windows launcher accepts `-GuardianPath` or the `PYGUARDIAN_CMD` environment
variable and also checks for `PyGuard.cmd` on PATH. On Tom's workstation, run
`Start-SumoEditor.cmd` in the viewer folder. It starts through Guardian and opens
the browser; `Stop-SumoEditor.ps1` stops it gracefully. Guardian's job worker is
serial: stop the editor before submitting more supervised Python jobs.

## 2. Package layout

```text
ontolomerge/
  README.md, LICENSE, THIRD_PARTY_NOTICES.md, PACKAGE_MANIFEST.json
  ontolomerge_v0_1_<date>.html
  Start-SumoEditor.cmd                 # optional Windows/Guardian launcher
  code/
    serve_sumo_editor.py, sumo_editor.py, sumo_editor_ui.js
    serve_ontolomerge.py, export_ontolomerge_data.py, ontolomerge.html
    Start-SumoEditor.ps1, Stop-SumoEditor.ps1
    review_provisional.py, boot_test_stub.js
    test_sumo_editor.py, test_sumo_editor_browser.mjs
  data/
    ontolomerge_public.sqlite
    *.tsv, viewer_overlays.json
  sumo_src/
    *.kif, README.txt                  # unmodified upstream source snapshot
  docs/
    USER_MANUAL_ONTOLOMERGE_FK12.md, INSTALL_ONTOLOMERGE.md
    SUMO_EDITOR_README.md, YOUTUBE_SCRIPT_ONTOLOMERGE.md
    SCREENSHOT_PLAN.md
```

Internal development keeps the code in `lcc_map/viewer/`, the mapping DB one level
above, and sources in `lcc_map/sumo_src/`. The same servers resolve either layout.
No internal database or existing editor workspace is shipped in the GitHub zip.

## 3. SUMO editing workflow

Open **SUMO editor**, or right-click a SUMO class. Add subclasses, edit documentation
or move a subtree. Rename/delete are restricted to unreferenced local leaves.

Preview → save proposal → preview the queue item → check the review box → Apply
locally or Reject. Apply revalidates, backs up the workspace and reloads the tree.
Stale proposals must be rejected and resubmitted against the current revision.

This release edits the 500-class mapped snapshot. All 74 packaged KIF files inform
cycle/reference checks. Depths and depth-3 branch anchors follow shortest paths in
the Merge.kif taxonomy. Secondary parents are retained when moving a class.
Affected existing mapping evidence is flagged for review, not automatically changed.

KIF downloads contain real unified source diffs, complete changed files and an audit
record. Source line endings and hashes are preserved. Subclass assertions are
round-trip checked. This is not arbitrary axiom editing or theorem proving.

## 4. Workspace storage, backup and recovery

The default is `code/editor_workspace/sumo_editor.sqlite` in the package, or
`viewer/editor_workspace/sumo_editor.sqlite` internally. It contains the frozen
baseline, KIF sources, current edited tree and proposal history. Pre-apply backups
are under `editor_workspace/backups/`.

Reopening the editor resumes the same workspace. Regenerating the viewer does not
rebase existing edits onto newer mapping data. Use a distinct workspace for a new
baseline or for a recovered backup:

```bash
python code/serve_sumo_editor.py --workspace ./my-workspace.sqlite --port 41774
```

Copy a backup to a **new** filename, then pass that filename with `--workspace`.
Retain the current file and history. Never run mutation tests against a live workspace.
Workspace files, backups and personal proposals are intentionally excluded from
the release zip and from the package's Git ignore rules.

## 5. Regenerate the viewer

From the extracted package root:

```bash
python code/export_ontolomerge_data.py --public
node code/boot_test_stub.js ontolomerge_v0_1_<date>.html
```

The exporter reads the packaged DB read-only and writes a new dated HTML at the
package root. Internal exports still default to the viewer folder. The public
overlay file preserves the bastard-child and relabel-plan layers on regeneration.
The exporter reads authoritative relations from `final_link.final_relation`.

After every template change or re-export, the boot test must pass: completed render,
well-formed stats, label masks in correct paint order and no risers crossing label
dot zones. Do not ship a failing artifact. Public builds omit per-reviewer data.

## 6. Public data and provenance

The public database includes only viewer nodes/edges, published link grades/status,
direction/corroboration counts, hole identities and an empty mapping proposal table.
Nomination tables, reviewer identities, vote text and internal decision commentary
are excluded. Frozen public overlays retain counterexamples and visible fault flags.

The KIF snapshot is copied byte-for-byte with upstream notices. Its source hashes
and snapshot identifier are in the package manifest. SUMO's own licensing/credit
notices are separate from the MIT license on OntoloMerge code and mapping relations;
see `THIRD_PARTY_NOTICES.md` and the original KIF headers/README.

## 7. Mapping proposals and review

Dragging between opposite trees proposes a mapping link. Double-clicking a link
proposes a change or retirement. These operations write `provisional_link` only.
They recognize published classes; new local class mapping is not yet integrated.

```bash
python code/review_provisional.py list
python code/review_provisional.py approve 3 --initials TS
python code/review_provisional.py reject 4 --initials TS --reason "duplicate"
```

These commands change proposal status and reviewer attribution. They do not promote
approved proposals into `final_link`. SUMO class-edit review takes place in the
editor panel, separately from this mapping-link CLI.

## 8. APIs

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Mode, build stamp and editor session token where applicable |
| `/api/provisional` | GET | Pending mapping proposals |
| `/api/propose` | POST | Propose a mapping create/modify/delete |
| `/api/class_edits` | GET | SUMO edit history and current revision |
| `/api/preview_class_edit` | POST | Validate a class edit and report before/after impact |
| `/api/propose_class_edit` | POST | Save a pending class edit |
| `/api/decide_class_edit` | POST | Apply or reject with reviewer initials/revision |
| `/api/sumo_delta.zip` | GET | Export applied KIF changes |
| `/api/editor_shutdown` | POST | Gracefully stop the editor |

Class-edit POST requests require JSON, the same origin and the health response's
token in `X-OntoloMerge-Token`. A stale revision or invalid edit returns an error
without applying the change. These APIs are for local use, not a hosted multiuser service.

## 9. Validation

Stop any Guardian-supervised server before submitting checks through Guardian.
For a standalone Python installation, from the extracted package root:

```bash
python code/serve_sumo_editor.py --check
python code/test_sumo_editor.py
```

The suite uses temporary workspaces and requires Git for its source-patch check.
The optional `--browser` check also needs Node 24+ and installed Chrome on Windows:
it verifies preview, save, overlay, review, Apply, reload and KIF download using a
disposable browser profile and workspace. It does not change the user's workspace.
Set `CHROME_PATH` to use a custom Chrome executable; otherwise the browser check
uses Chrome under the Windows `ProgramFiles` directory or `google-chrome` on PATH.

## 10. Troubleshooting

- **No editor button:** you opened the static file or port 41771. Use port 41772.
- **Missing KIF sources/database:** extract the whole zip; do not move `code/` alone.
- **Port busy:** use `--port 41774` and open the matching URL.
- **Workspace changed:** refresh and re-propose against the current revision.
- **Guardian job queued indefinitely:** stop a running supervised server first.
- **Local class cannot be mapped:** that integration is not in this release.
- **Upstream rename/delete refused:** this tree editor does not rewrite arbitrary
  rules, domains, disjointness or instances. Use a full axiom-aware workflow.
- **Relations appear stale after a tree move:** the warning is intentional; mapping
  reconciliation has not been rerun.
