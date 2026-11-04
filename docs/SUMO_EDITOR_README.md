# SUMO editor — quick guide

**modsource:** ontolomerge_github_editor_v0_3_20261103

From the extracted package's `ontolomerge` folder, run:

```bash
python code/serve_sumo_editor.py
```

Open **http://127.0.0.1:41772/**. Guardian users should launch the Python file
through Guardian. `Start-SumoEditor.cmd` is an optional Windows/Guardian launcher;
set `PYGUARDIAN_CMD` to your installed `PyGuard.cmd`, or put it on PATH.

## Make a reviewed change

1. Right-click a SUMO class, or open **SUMO editor** in the top bar.
2. Choose Add subclass, Edit documentation, Move, Rename local leaf or Delete local
   leaf. Add requires a capitalized name, parent and English definition.
3. Enter initials and the reason/evidence. Optional extra parents are comma separated.
4. **Preview change** reports before/after content and impact without saving.
5. **Save proposal** records a pending edit; the tree has not changed yet.
6. In the queue, **Preview #…**, check the review box, then **Apply locally** or
   **Reject**. Apply revalidates, backs up and reloads the tree.
7. **Download KIF changes (.zip)** exports applied edits for maintainer review.

Drag SUMO → SUMO to prepare a move. Drag between SUMO and LCC to propose a mapping
link using the existing link workbench. These are different operations and review
queues. The mapping API currently recognizes published classes only.

## Scope

This is the 500-class mapped SUMO snapshot. The bundled 74 KIF files inform cycle
and reference checks, including secondary and out-of-view paths. Moves preserve
secondary parents. The displayed tree follows shortest paths from Entity, so its
displayed parent can change when another retained parent offers a shorter route.

Upstream class rename/delete and arbitrary axiom editing are not implemented.
Rename/delete are restricted to local leaves without dependent children or published
links. Entity cannot be moved, deleted or renamed. Stale proposals must be rejected
and resubmitted against the current tree revision.

Affected existing classes carry a mapping-review warning. The published mapping,
holes and bastard evidence stay visible; the editor does not reconcile them or
prove the revised ontology logically consistent.

## Workspace and export

`code/editor_workspace/sumo_editor.sqlite` holds your baseline, edited tree and
audit history. Pre-apply backups are in its `backups/` folder. Keep both out of
public commits. Restarting resumes that workspace; it does not rebase it onto a
newer mapping automatically. Use `--workspace ./another.sqlite` for a separate
workspace. To recover, copy a backup to a new filename and open that copy.

The KIF download contains a unified patch, complete changed files and an audit
record. Moves remove the old axiom and add the replacement; English documentation
statements are replaced. Source line endings are preserved. The exporter checks
the complete expected and actual subclass assertion sets, including out-of-view
classes, before producing the zip. This is structural verification, not a logical
proof or upstream acceptance.

Ctrl+C stops an ordinary terminal server. Guardian users can run
`code/Stop-SumoEditor.ps1` to stop gracefully; stop long-running supervised servers
before queueing more Python work through Guardian.

See the [user guide](USER_MANUAL_ONTOLOMERGE_FK12.md) for navigation and figures,
and the [operations guide](INSTALL_ONTOLOMERGE.md) for APIs, tests and recovery.
