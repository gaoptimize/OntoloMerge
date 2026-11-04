# OntoloMerge production shot plan — release 0.3

**modsource:** ontolomerge_github_editor_v0_3_20261103  
Packaged as `docs/SCREENSHOT_PLAN.md`.

This replaces the prior viewer-only shot plan. Match the updated user guide and
14-scene narration. The first ten figure groups cover the map; four new groups
cover the SUMO editor. Figure slots in the guide remain specifications until the
corresponding production image is shot.

## Setup

Use the **public GitHub package**, a modern browser at 1600×1000 or larger, and
100% zoom. Use the current renderer: label masks and shared riser channels must
be visible. Do not use older shots with lines crossing text.

Run all example mutations in a **separate disposable workspace**:

```bash
python code/serve_sumo_editor.py --workspace ./demo-workspace.sqlite --port 41774
```

On a Guardian workstation, submit that command through Guardian and stop other
supervised servers first. Do not use the live ontology workspace or publish its
history. Use `DemonstrationClass`, initials `DEMO`, and the note “video example”.
Label it as a fictional local class. Existing SUMO definitions must not be changed
merely to prepare a camera shot.

## Required shots

| File | Guide | Capture |
|---|---|---|
| fig01_overview.png | §1 | Whole window, IntentionalProcess, bar and legend |
| fig01b_faded.png | §7 | Same branch, Alt+wheel fade near 0.3; status visible |
| fig02_ribbons.png | §3 | Several ribbon colors and legend |
| fig03_rings.png | §4 | Red hole, amber bastard ring, evidence tooltip |
| fig03b_marquee.png | §7 | Right-drag zoom box over empty canvas/map |
| fig04_lcc_tip.png | §6 | Insurance LCC tooltip with schedule notes |
| fig05_sumo_tip.png | §6 | Full SUMO documentation tooltip |
| fig06_search.png | §7 | Search results with displayed ancestry |
| fig07a_before.png / fig07b_after.png | §7 | Focus before and after |
| fig08_drag.png | §9 | Mapping drag between opposite trees |
| fig09_dialog.png | §9 | Mapping proposal dialog and initials |
| fig10_provisional.png | §9 | Pending mapping link and retirement marker |
| fig11_editor.png | §10 | Add-subclass panel with name, parent, documentation, DEMO |
| fig12_preview_queue.png | §11 | Before/after preview, pending proposal and its dashed parent ring |
| fig13_local_class.png | §11 | Applied local class, LOCAL CLASS tooltip, revision/history |
| fig14_kif_export.png | §13 | Download link plus patch/KIF/audit contents; removed/added edge lines |

## Video-only actions and checks

- Capture SUMO → SUMO drag and the move preview, not a drag across the two trees.
- Capture a refused upstream rename/delete and the reason; no destructive action
  should succeed for that shot.
- A pending added class is represented by a ring on its parent; it does not appear
  as a new node until Apply. Keep that sequence clear.
- Keep **Preview #… → review box → Apply locally** legible in the queue.
- Show a changed upstream class's mapping-review warning if using an approved
  disposable example. Do not imply the mapping was automatically reconciled.
- KIF export is a download, not an upload or upstream approval. Never film a real
  publication/commit as part of this demonstration.

Check every image for intact labels, no hierarchy strike-through and no riser
inside a nomination-dot zone. No reviewer identities, private workspace history,
machine-specific paths or internal editorial commentary should be visible.

The final contribution-credits card is an intentional exception for named roles:
use the exact card in the narration file, including Tom Schaefer's requested
credit, “ideation and human advisor”. Do not expose per-link reviewer records.
