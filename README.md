# OntoloMerge 0.4

Explore the complete pinned SUMO KIF collection alongside Library of Congress
Classification: **145 files, 10,415 reachable classes, 213,140 assertions and
5,295 existing mapping links**.

[Download the latest release](https://github.com/gaoptimize/OntoloMerge/releases/latest)
· [November 3 Initial release](https://github.com/gaoptimize/OntoloMerge/releases/tag/initial)

The additional classes expand what you can inspect and edit. They have **not all
been mapped to LCC**. Existing mapping decisions and their original depths remain
distinct from depths in the expanded source graph. All-files mode includes
experimental and test sources; use the graph selector to choose root modules or
the Merge foundation. Another 47 disconnected classes remain in the source catalog.

## Start

Download the release ZIP, extract it completely, and open
`code/ontolomerge_v0_4_20261105.html` for offline read-only viewing.

For source-assertion search, mapping proposals and the reviewed local SUMO editor,
run this from the extracted `ontolomerge` folder with Python 3.10 or newer:

```sh
python code/serve_sumo_editor.py
```

Open **http://127.0.0.1:41772/**. The server uses only the Python standard library,
binds to your own computer, and requires no model service. Stop with Ctrl+C.
If your workstation requires Python Guardian, run through Guardian instead;
the optional Windows launcher accepts its path through `PYGUARDIAN_CMD`.

## Navigation

- Select a graph scope, source file, branch and depth, including All depths.
- Click a class to isolate its subtree; search finds classes by name.
- Use **Left/Right arrows** or **◀/▶ buttons** to step between measured columns.
  Rapid steps coalesce into one viewport update, without intermediate graph layouts.
- **Fit** restores the complete branch. Drag to pan, wheel to zoom; Alt+wheel fades links.
- **Sources & instances** lists source hashes, roles, disconnected classes, named
  instance counts and examples. With the server running, search the complete
  assertion text with file and line references.

## Editing and upgrading

Right-click a SUMO class or open SUMO editor: preview → propose → review → apply
locally → export KIF. Original KIF files and published mappings are not rewritten.
Rename/delete are restricted to local leaves. Exported patches require review;
the application does not prove logical consistency or automatically reconcile maps.

Extract this version into a **new folder**, retaining your old installation and
workspace. This package contains no personal workspace, proposal history or
credentials. A fresh workspace is created under `code/editor_workspace` on first
editor startup. Existing workspaces are not automatically migrated by this public
package; preserve the old folder if you have edits to carry forward.

## Release history and attribution

The Initial release remains available at its original tag. Version 0.4 expands
source coverage, repairs two missed multiline subclass statements, adds discrete
column navigation, and speeds exact crossing counts. See [CHANGELOG.md](CHANGELOG.md),
[CREDITS.md](CREDITS.md), [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
