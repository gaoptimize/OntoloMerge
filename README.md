# OntoloMerge

**A SUMO ↔ LCC map, mapping workbench and reviewed SUMO tree editor.**

OntoloMerge shows 500 SUMO classes, about 6,900 Library of Congress outline rows,
and 5,295 graded mapping links. Inspect holes, bastard-child evidence, definitions,
library schedule notes and the claims connecting the two systems.

The SUMO editor adds a path from a discovered problem to a concrete proposed
correction: **preview → propose → review → apply locally → export KIF**.

## Start

Open the dated HTML file for offline, read-only viewing. To edit, extract the whole
package, open a terminal in its `ontolomerge` folder and run:

```bash
python code/serve_sumo_editor.py
```

Open **http://127.0.0.1:41772/**. Python 3.10+ is required; the application uses
the standard library and makes no model calls. On a Python Guardian workstation,
launch the file through Guardian. The optional Windows launcher uses Guardian
from PATH, `PYGUARDIAN_CMD`, or an explicit `-GuardianPath` setting.

For the mapping-only workbench, use `python code/serve_ontolomerge.py` and port 41771.

## SUMO editing

- Right-click a SUMO class or choose **SUMO editor**.
- Add a local subclass, edit English documentation, or move a subtree.
- Retain secondary parents; refuse cycles through visible and out-of-view parents.
- Review each proposal before applying it to a separate local workspace.
- Keep backups, revisions and an attributed decision history.
- Export a real KIF source diff, complete changed files and a structural audit.

Rename/delete are restricted to local leaves. This release edits the mapped
500-class snapshot, not arbitrary SUMO axioms. It does not automatically reconcile
mapping changes or prove logical consistency. New local-class mapping is a remaining
integration step. Exported patches still require maintainer review.

The original SUMO files and published mapping are not rewritten by tree editing.
Personal workspaces and test proposals are not included in this release.

## Map features

Ribbon colors grade link relations; direction dots show nomination direction.
Red rings mark holes and amber rings mark bastard-child evidence. Tooltips expose
definitions, counterexamples and LCC schedule notes. Search, focus, branch/depth
controls, crossing reduction and Alt+wheel fading help inspect dense branches.

## Guides and narration

- [User guide](docs/USER_MANUAL_ONTOLOMERGE_FK12.md)
- [Install and operations](docs/INSTALL_ONTOLOMERGE.md)
- [SUMO editor guide](docs/SUMO_EDITOR_README.md)
- [YouTube/ElevenLabs cued script](docs/YOUTUBE_SCRIPT_ONTOLOMERGE.md)
- [Screenshot and demonstration plan](docs/SCREENSHOT_PLAN.md)
- [Contribution credits](CREDITS.md)

## Rebuild and check

```bash
python code/export_ontolomerge_data.py --public
node code/boot_test_stub.js ontolomerge_v0_1_<date>.html
python code/serve_sumo_editor.py --check
python code/test_sumo_editor.py
```

The exporter reads the public database and frozen TSVs, preserving the packaged
hole/bastard and relabel layers. Tests use disposable workspaces; Git is required
for the source-patch check. The optional browser suite needs Node 24+ and Chrome
on Windows. See the install guide before running tests through Guardian.

## Credits and licenses

SUMO: [Ontology Portal](https://www.ontologyportal.org), including its IEEE and
other upstream source notices. LCC: Library of Congress outline and schedule
material. Source snapshot and file hashes are recorded in `PACKAGE_MANIFEST.json`.

OntoloMerge software and mapping relations are distributed under the included MIT
license. Upstream SUMO source keeps its original notices; see
`THIRD_PARTY_NOTICES.md`, `sumo_src/README.txt` and individual KIF headers.

**Tom Schaefer — ideation and human advisor.**

Original viewer and initial package: **Kimi**. Mapping and independent checks:
**Claude, Grok and GPT/Astra**. SUMO editor, release enhancement and revised guides:
**GPT/Codex**. See [CREDITS.md](CREDITS.md) for roles and source acknowledgments.

<!-- modsource: ontolomerge_github_cued_script_20261103 -->
