# OntoloMerge User Manual

**Viewer, mapping workbench and SUMO tree editor · release 0.3**  
**modsource:** ontolomerge_github_cued_script_20261103  

## 1. What you are looking at

OntoloMerge connects two systems for organizing knowledge. SUMO is the Suggested
Upper Merged Ontology. LCC is the Library of Congress Classification.

- The left side shows the **500 SUMO classes in this mapped snapshot**. SUMO as a
  whole contains many more classes; this is not its entire ontology.
- The right side shows about 6,900 LCC outline rows, with codes and captions.
- Between them are 5,295 graded mapping links. Each link records a claim about how
  a class relates to a library category.
- You normally view one SUMO branch and its mapped LCC rows at a time.

**[FIG-01]** Whole window, IntentionalProcess branch, top bar and legend visible.

## 2. Three ways to use it

| Mode | Open | What you can change |
|---|---|---|
| Viewer | The dated HTML file in your browser | Nothing; it works offline |
| Mapping workbench | Local server on port 41771 | Propose, modify or retire mapping links |
| SUMO editor | Local server on port 41772 | Propose and review changes to the SUMO tree, plus use the mapping controls |

For the GitHub package, start the editor from the extracted package folder:

```bash
python code/serve_sumo_editor.py
```

Then open **http://127.0.0.1:41772/**. If you use Python Guardian, launch that file
through Guardian instead. On Tom's workstation, use `Start-SumoEditor.cmd`.
The installation guide explains both layouts and the Guardian launcher.

## 3. The ribbon scale

| Color | Relation | Meaning |
|---|---|---|
| Blue | exact | The two categories cover the same ground |
| Red | broader | The SUMO class contains the LCC category |
| White, gray outline | narrower | The SUMO class covers less ground |
| Yellow | partial | They overlap without a containment claim |
| Green | generic | A general association |
| Pink | related | A weaker relatedness claim |
| Gray | none | No positive mapping claim |

Line weight and brightness reinforce the scale. **[FIG-02]** Several ribbon colors
with the legend visible.

## 4. Direction dots, holes and bastard children

A dark dot after a label marks the side that nominated a link. A dot at each end
means it was found from both directions. This is corroboration, not a correctness
guarantee.

A **red ring** marks a hole: an unmapped node. An **amber ring** marks what the
project calls a **bastard child**: a SUMO class for which the mapping process found
no adequate LCC home. Hover to inspect the evidence. Where an underlying SUMO fault
was separately verified, the tooltip says so. An unmapped class alone does not prove
that SUMO is wrong.

**[FIG-03]** A hole and bastard-child ring, with the evidence tooltip open.

## 5. Planned relabel overlay

A black dotted underlay marks a difference between a recorded relabel plan and the
current mapping. It does **not** change the ribbon's authoritative relation.
Some plan entries can be superseded by later rulings. Treat this as an editorial
comparison layer, not proof that the present relation is wrong.

Use **relabel plan overlay** to hide or show it. The packaged snapshot includes
the overlay and bastard-child evidence; regenerating from the packaged inputs
preserves them.

## 6. Reading the trees and tooltips

Labels are not truncated. Columns fit the longest label at each depth. Hierarchy
lines stop at label boundaries so they do not strike through words.

SUMO allows several parents: it is a directed graph, not a single-parent tree.
The displayed parent uses a solid line; secondary parents use faint dashed lines.
The **secondary SUMO parents** control shows or hides those extra edges.

Hover a SUMO label to read its documentation. Hover an LCC row to read its code,
caption and available schedule notes. Hover a link to inspect its relation,
direction, status and corroboration count.

**[FIG-04]** LCC tooltip on insurance with schedule notes.  
**[FIG-05]** SUMO tooltip with its documentation paragraph.

## 7. Navigation, search and focus

- **Left-drag empty canvas:** pan.
- **Mouse wheel:** zoom around the pointer.
- **Alt + mouse wheel:** fade or restore the mapping lines. The status line shows
  the active fade level.
- **Right-drag:** draw a zoom box. In the SUMO editor, a right-click without a drag
  on a SUMO class opens its editor.
- **Click a node:** focus on its subtree and the mapped counterparts with their
  ancestry. Click the focus chip's ×, press Escape or change branch to release it.

Search matches SUMO class names and LCC codes or captions. Each result shows its
displayed ancestry, from the selected node back toward the root. Click a result
to focus it. Search can find local additions beyond the branch depth filter.

**[FIG-06]** Search results with ancestry. **[FIG-07a/b]** Before and after focus.

## 8. Top bar controls

**branch** selects a branch. **depth** caps the SUMO side at five or six in branch
view; it does not filter LCC rows. Some branches have no depth-six additions, so
changing this control may leave their counts unchanged. Changing depth releases
an active focus.

**hide implied links** suppresses links tagged as implied. This tag is an editorial
heuristic, not a theorem-prover result. Other controls toggle secondary parents,
the relabel plan and provisional mapping links. The status line reports node/link
counts and crossings before and after the layout's ordering pass.

## 9. Propose a mapping link

In either server mode, drag between opposite sides of the map. The link proposal
dialog asks for the relation, your initials (2–4 letters) and an optional reason.
Double-click an existing link to propose a modification or retirement.

Proposed links appear as teal dashes; a proposed retirement has a red ×. The
published mapping is not changed. A separate review command can mark a proposal
approved or rejected; approval alone does not insert it into the published mapping.

The current mapping API recognizes the original published classes. Mapping a newly
added local class is not yet integrated.

**[FIG-08]** Mapping drag. **[FIG-09]** Link dialog. **[FIG-10]** Pending link marks.

## 10. Edit the SUMO tree

Open **SUMO editor** in the top bar, or right-click a SUMO class. The side panel
offers five operations:

| Operation | What it does |
|---|---|
| Add subclass | Adds a local class under an existing parent; name and English documentation are required |
| Edit documentation | Proposes a new English definition for an existing class |
| Move | Replaces its displayed parent, retaining secondary parents and descendants |
| Rename local leaf | Renames a class created in this workspace if it has no dependent children or published links |
| Delete local leaf | Removes such a local class from the current workspace tree while retaining its history |

Optional secondary parents for an addition are comma separated. To prepare a move,
you can also drag a SUMO class onto another SUMO class. The panel confirms the target.

The displayed tree follows shortest paths from Entity. If another retained parent
gives a shorter path, it can become the displayed parent after a move. Cycles are
refused, including cycles through secondary parents and KIF classes outside the map.
Entity cannot be moved, renamed or deleted.

Upstream rename/delete is refused because a class may occur in rules, instances or
other axioms outside the tree. The refusal reports relevant counts.

**[FIG-11]** Add-subclass panel with documentation and initials entered.

## 11. Preview, propose, review and apply

1. Choose the class and operation. Enter your initials and reason/evidence.
2. Click **Preview change**. Read the before/after definition, parents, depth and
   impact counts. A preview makes no change.
3. Click **Save proposal**. It is now durable but remains pending.
4. In the review queue, click **Preview #…** for that proposal.
5. After reviewing it, check the review box and click **Apply locally**, or **Reject**.

Apply revalidates the proposal, creates a backup, records the decision and refreshes
the tree. A local addition appears with **LOCAL CLASS** in its tooltip. A proposal
made against an older tree revision cannot be applied; reject and resubmit it.

Pending additions mark their parent with a teal dashed ring. Documentation and
rename proposals mark the subject in teal; moves use amber and deletion uses red.
These editor rings are distinct from the map's solid hole/bastard rings. The queue
also identifies the operation in words. Pending additions enter the tree only after
Apply. After Apply, the changed class is focused even if it is deeper than six.

**[FIG-12]** Before/after preview and pending queue.  
**[FIG-13]** Applied local class with the LOCAL CLASS tooltip.

## 12. What changes, and what stays published evidence

Tree changes are saved in a separate local workspace. They do not rewrite the
original mapping database or SUMO KIF files. Backups and a timestamped history keep
the earlier state and reviewer attribution.

Edits can make mapping evidence stale. A changed upstream class, and affected
descendants of a move, receive a tooltip warning that their mapping/hole evidence
needs review. Existing links, holes and bastard-child evidence remain visible as
the published findings. OntoloMerge does not automatically rerun reconciliation or
prove the revised ontology logically consistent.

Reload other open tabs after applying an edit. Keep your workspace and backups out
of public commits unless you have intentionally reviewed their contents.

## 13. Send a KIF change for maintainer review

Choose **Download KIF changes (.zip)**. The download contains applied edits only:

- A unified source patch, including removed and added subclass assertions.
- Complete changed KIF files and a local additions file where needed.
- An audit record with decisions, source hashes and structural verification.

Before export, the editor reparses the result and checks the expected subclass
assertions against the actual ones, including out-of-view classes. This catches a
missing removal or an unintended added edge. It is not a full logical consistency
check. Review the changed axioms using the SUMO maintainers' normal tools.

The download does not publish anything or modify an upstream checkout. A patch is
a proposed source change; an upstream maintainer still decides whether to accept it.

**[FIG-14]** Export link and extracted patch/KIF/audit files.

## 14. Quick reference

Open the HTML for viewing. Use port **41771** for mapping proposals, or **41772**
for the SUMO editor. Right-click a SUMO class to edit; drag SUMO → SUMO to prepare
a move; drag SUMO ↔ LCC to propose a mapping link. Preview → propose → review →
apply locally → export KIF. For installation and recovery, see
`INSTALL_ONTOLOMERGE.md` and `SUMO_EDITOR_README.md`.
The companion `YOUTUBE_SCRIPT_ONTOLOMERGE.md` contains the expression-cued
narration and SUMO Director's Cut production notes.

## 15. Credits

**Tom Schaefer — ideation and human advisor.** Kimi built the original viewer,
layout, workbench and package and drafted the SUMO editor plan. Claude, Grok and
GPT/Astra contributed the mapping and independent checks. GPT/Codex implemented
the SUMO editor, enhanced the release package and revised these guides and narration.
SUMO's maintainers and contributors provide the ontology; the Library of Congress
provides the classification material. Full roles and source acknowledgments are
in the package's `CREDITS.md` and `THIRD_PARTY_NOTICES.md`.
