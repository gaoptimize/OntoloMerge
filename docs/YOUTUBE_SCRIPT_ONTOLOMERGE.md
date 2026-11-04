# OntoloMerge: from mapping evidence to SUMO editing (Initial)

**ElevenLabs narration script · v0.2: expression-cued (Eleven v3 audio tags)**  
**Base:** `YOUTUBE_SCRIPT_ONTOLOMERGE_v0_1.md` (release 0.3 revision, modsource ontolomerge_github_editor_v0_3_20261103). That file is untouched. The narration **wording of Scenes 1–14 is identical** (verified word for word), **except for one added line in Scene 11** (the honest-experiment line, a DRAFT). Cues were added and shot notes reformatted. **New narration, all marked DRAFT for Codex and maintainer review: Scene 1b (the SUMO primer), Scene 13b (the seven link classes and when to use each) and that Scene 11 line.**  
**modsource:** ontolomerge_script_v0_2_elevenlabs_cues_20261103 (Claude, at Tom's request)  
**Length:** allow roughly 9–11 minutes including demonstrations and pauses. The cues add pauses, so **re-time after a test render**.

## Production notes (not narrated)

- **This is the "Initial" release video** (Tom, 2026-11-03). The 2026-11-03 footage (`docs/figs_20261103/`) is usable but **cluttered**: most map frames show the whole branch, with hundreds of overlapping yellow `partial` ribbons.
  - **Next shoot:** every map frame must first **focus** on the subject of the scene. Click the LCC row or SUMO class of interest; Escape releases. Where links still crowd, also fade them with **Alt+wheel**.
  - **Suggested focus subjects:** Scene 1 an IntentionalProcess subtree; Scene 3 the `Designing` misfit and its counterexample row; Scene 7 one SUMO class and one LCC row; Scene 11 `Residence`.
  - The shot plan (`SCREENSHOT_LIST_FOR_GROK.md`, Codex's file) should be amended to require this before the next shoot.

- **Model:** cues are written for **Eleven v3**, which reads `[square-bracket]` audio tags as performance directions.
  - On **v2 / Multilingual / Flash**, strip every `[…]` and turn each `[short pause]` / `[long pause]` into `<break time="0.6s" />` / `<break time="1.2s" />`. v3 ignores `<break>`.
- **Shots are no longer in square brackets.** Each scene's shot note is now a `> Shot:` blockquote. **Every `[…]` left in a narration paragraph is an ElevenLabs tag**, so you can paste narration paragraphs as they are. Don't paste headings or blockquotes.
- **Voice:** a calm, clear documentary voice. Tags nudge the delivery; they don't change the character. With v3, set **Stability to "Natural"**. "Robust" largely ignores tags, and "Creative" over-acts them.
- **Tag vocabulary** is kept small so the read stays consistent:

  | Tag | Use |
  |---|---|
  | `[calm]` | default documentary register; scene openings |
  | `[warmly]` | invitations to the viewer, the close |
  | `[curious]` | a question raised, the start of a demonstration |
  | `[thoughtful]` | the one idea to remember in a scene |
  | `[matter-of-fact]` | controls and keystrokes, operational steps |
  | `[serious]` | limits, cautions, "this does not prove…" |
  | `[lightly amused]` | used once, on "bastard child" |
  | `[short pause]` / `[long pause]` | breath before a key line / scene-end beat |

  These are interpreted directions, not a fixed API list. **Render Scene 3 and the Final Slide as a test first.** If a tag is voiced aloud or ignored, swap it for a plainer emotion (`[calm]`, `[thoughtful]`) or an ellipsis.
- **Ellipses (…) and em dashes** are added sparingly for breath; v3 honours both. Paragraph breaks give a natural beat.
- **Pronunciation:**
  - SUMO = "soo-moh", which v3 normally gets right.
  - **KIF** is read as one word, "kiff". If the render spells it out, add a pronunciation dictionary entry; don't respell it in the script.
  - **LCC** isn't spoken in the narration.
- **Unchanged from v0.1:**
  - Use the public release artifact and an extracted-package editor.
  - Record class mutations in a **disposable demonstration workspace**, never the working ontology.
  - **DemonstrationClass** is a local example, and the initials **DEMO** are demonstration attribution only.
  - Show the 500-class **mapped snapshot**; don't describe it as all of SUMO.
  - The video demonstrates software behaviour, not upstream acceptance or a proof of consistency. Keep the limits in Scene 13.
  - Record and publish only when Tom directs.
- **Footage gate:** Grok's 12-frame re-shoot should use Kimi's re-export after Claude's 2026-11-03 DB changes. The narration quotes no counts, so it doesn't change.

---

## SCENE 1: Two trees, and now an editor [budget: 40 seconds]

> **Shot:** fig01 overview. End on the SUMO editor button.

> ✂ **Director's Cut: IN.** All of Scene 1.

[calm] You are looking at two ways of organizing knowledge.

On the left, SUMO, a formal ontology. This map shows five hundred of its
classes, from objects and processes to intentions and relations. [short pause] On the right,
the Library of Congress Classification: about sixty-nine hundred outline rows
describing where books belong.

[thoughtful] The lines between them are claims about how those categories relate. [short pause] This is
OntoloMerge. It began as a way to inspect the mapping. [curious] Now it also lets you
propose changes to the SUMO tree, review them, and export actual KIF changes
for the ontology's maintainers.

## SCENE 1b: What SUMO is (primer, NEW DRAFT) [budget: 30 seconds]

> ✂ **Director's Cut: IN.** In both cuts. **New narration** (Claude, 2026-11-03, at Tom's request: *"SUMO hasn't done a very good marketing job… 30 seconds would help this AND broaden the audience"*).
> **Status: DRAFT for review.** Codex is to check it, and SUMO maintainers are explicitly invited to edit it. Every factual claim is listed with its source in the fact sheet below.

> **Shot:** zoom the SUMO side of fig01 to its root (Entity → Physical / Abstract, then Object / Process). Cut to a documentation tooltip (fig05). Then show one real KIF line on screen, e.g. `(subclass Tissue BodySubstance)` (Merge.kif l.19608).

[warmly] So what is SUMO? [short pause] [calm] The Suggested Upper Merged Ontology is a free, formal map of meaning, built and refined for more than twenty years. It begins with the most general ideas, physical and abstract, objects and processes, and branches down to the specific. [matter-of-fact] Every class carries an English definition, and every claim is written as a logical statement in KIF, so a machine can reason with it. [thoughtful] With its domain ontologies, SUMO spans more than fifteen thousand terms, and it is mapped to the whole of WordNet.

> **Primer fact sheet** (not narrated; for Codex and the SUMO maintainers to check):
>
> | Claim | Evidence |
> |---|---|
> | Name: Suggested Upper Merged Ontology | ontologyportal.org (README in `lcc_map/sumo_src/`) |
> | "free" | sumo_src README: released under the GNU license, with a credit requirement. **Maintainers: is "free" the word you want?** |
> | "more than twenty years" | IEEE Standard Upper Ontology working group origin, c. 2000–2001. **To confirm** |
> | Physical / Abstract at the top | Merge.kif l.915 `(partition Entity Physical Abstract)` (active) |
> | objects and processes | `Object` and `Process` are both subclasses of `Physical`. Their *partition* axiom is commented out (l.934), so the script says neither "disjoint" nor "partition" |
> | English definition for every class | `(documentation <Term> EnglishWrittenLanguage "…")`: 1,378 such statements in Merge.kif alone. **"Every" to be verified by maintainers;** soften to "Classes carry…" if there are gaps |
> | KIF, a machine can reason with it | SUO-KIF. Sigma KEE runs automated theorem provers over it (README: "SigmaKEE"). |
> | more than fifteen thousand terms | measured 2026-11-03 over the local non-gazetteer `.kif` files: ≥16,358 terms named in subclass/instance statements (a lower bound), and about 66,000 top-level statements. Merge.kif alone: about 1,300 terms. |
> | mapped to the whole of WordNet | `sumo_src/WordNetMappings/WordNetMappings30-{noun,verb,adj,adv}.txt` (82,241 noun lines) |
>
> **Length:** 87 words ≈ 35 s at 150 wpm (measured). Maintainers trimming it is welcome.

## SCENE 2: The ribbon scale [budget: 45 seconds]

> ✂ **Director's Cut: OUT.** Skip Scene 2 and the first paragraph of Scene 3. Keep the legend visible in the Scene 3 footage, so the ribbon colors still read.

> **Shot:** fig02 ribbons; hold the legend in frame.

[warmly] Every link is colored like a fair ribbon. [matter-of-fact] Blue means exact: the two categories
cover the same ground. Red means the SUMO class is broader than the library row.
White, outlined in gray, means narrower. Yellow means partial overlap. Green is
generic, pink is related, and gray records no positive mapping claim.

[calm] Line weight and brightness reinforce the grade. They help you read the pattern
before you inspect any individual claim. [short pause] [serious] They do not turn a claim into proof.

## SCENE 3: Dots, holes and bastard children [budget: 50 seconds]

> **Shot:** direction dots, then fig03 rings and evidence tooltip.

[calm] A dark dot after a label marks the side that nominated a connection. Dots at
both ends mean it was found from both directions.

> ✂ **Director's Cut: IN.** From here to the end of Scene 3.

[calm] A red ring marks a hole: something with no mapped counterpart. An amber ring
marks what the project [lightly amused] bluntly calls a bastard child, [calm] a SUMO class for which
the mapping found no adequate home in the library classification.

[curious] Hover it. [matter-of-fact] The tooltip shows the counterexample and where the class fell out of
the mapping. Some cases also carry a separately verified SUMO fault. [serious] A gap alone
does not prove an ontology error. [short pause] [thoughtful] The value is that the evidence is exposed,
where a person can inspect it and decide what to do next.

> ✂ **Director's Cut: OUT.** Skip Scenes 4, 5 and 6; resume in Scene 7.

## SCENE 4: An editorial layer, not a verdict [budget: 25 seconds]

> **Shot:** relabel plan checkbox and one black dotted underlay.

[calm] A black dotted underlay compares an older relabel plan with the present mapping.
The ribbon still shows the authoritative current relation. Later rulings may
have superseded a plan entry, so the dots are an editorial prompt, [short pause] not a verdict.
[warmly] You can switch the layer off whenever you want a clearer view.

## SCENE 5: Readable trees and documentation [budget: 45 seconds]

> **Shot:** full labels and secondary edges; fig04 and fig05 tooltips.

[calm] The columns widen to fit their labels, and hierarchy lines stop at the edges
of the words. [thoughtful] Nothing is shortened to make the picture fit.

SUMO is a graph. A class can have more than one parent. [matter-of-fact] Solid lines show the
displayed tree; faint dashed lines show the extra parents.

[curious] Hover a SUMO class to read its documentation. Hover a library row to read its
caption and available schedule notes: class here, compare, see elsewhere.
[warmly] These are the library's own instructions, brought into the map where you need
them. [calm] Hover a link to inspect the claim between the two sides.

## SCENE 6: Move, search and focus [budget: 50 seconds]

> **Shot:** pan, wheel, zoom box, Alt+wheel fade; fig06 search; fig07 focus.

[matter-of-fact] Left-drag empty space to pan. Roll the wheel to zoom. Right-drag a box to zoom
straight into an area.

Hold Alt and roll the wheel to fade the links. [calm] In a dense branch, this lets
you read the trees through the ribbons… then bring the connections back.

[matter-of-fact] Search finds SUMO names and library codes or captions. Each result gives its
displayed ancestry back toward the root. Click a result, or any node, to focus
the picture on that subtree and its mapped counterparts. Escape releases the
focus. [calm] The branch selector and depth control let you choose the broader view.

## SCENE 7: Propose mapping links [budget: 40 seconds]

> **Shot:** fig08 drag across trees, fig09 link dialog, fig10 provisional marks.

> ✂ **Director's Cut: IN.** The first two paragraphs of Scene 7. Scene 8's "The second kind of editing…" needs this setup.

[calm] There are two kinds of editing here. [short pause] First, the mapping itself.

[matter-of-fact] Under a local server, drag from one tree to the other to propose a connection.
Choose the relation, enter your initials, and add your reason. Double-click an
existing link to propose a modification or retirement.

> ✂ **Director's Cut: OUT.** Skip the rest of Scene 7. Then **IN from Scene 8 to the end of Scene 14**, plus the Final Slide.

[calm] These are provisional proposals. Teal dashes and red retirement marks show
what is awaiting review. A separate review command records approval or rejection.
[serious] Approval does not automatically insert a proposal into the published mapping.

## SCENE 8: Open the SUMO editor [budget: 45 seconds]

> **Shot:** open port 41772; right-click a SUMO class; fig11 panel.

[curious] The second kind of editing changes the SUMO tree itself.

[matter-of-fact] Start the SUMO editor and open its local browser address. Click SUMO editor in
the top bar, or right-click a SUMO class. A panel opens beside the map.

[calm] You can add a subclass, edit its English documentation, or move a subtree.
Rename and delete are available for local leaf classes. The panel asks for your
initials and a reason, so the proposal remains attributable and reviewable.

[serious] For this demonstration, we are working in a disposable workspace. The example
class is local. It is not an addition already accepted into upstream SUMO.

## SCENE 9: Add, preview and propose [budget: 50 seconds]

> **Shot:** enter DemonstrationClass under IntentionalProcess, definition and DEMO; click Preview; fig12 before/after; save, show pending ring.

[matter-of-fact] Choose Add subclass. Give it a capitalized name, choose an existing parent, and
write the English documentation. [serious] A new class without a definition is refused.
[calm] If the class needs several parents, enter the additional ones here.

[curious] Click Preview change. [calm] You see the before and after: its name, parents, depth
and documentation, with the reported impact on existing classes and mapping
evidence. [short pause] Nothing has been applied.

[matter-of-fact] Save the proposal. It now survives a restart, but the tree has not changed.
[calm] A dashed teal ring marks the parent of the proposed addition, and the queue
shows the full proposal waiting for review.

## SCENE 10: Review and apply locally [budget: 50 seconds]

> **Shot:** queue Preview #; check review box; Apply locally; fig13 new class and tooltip.

[matter-of-fact] In the queue, preview that specific proposal again. [short pause] Read it. Check the review
box, then choose Apply locally, or Reject.

[calm] Apply rechecks the edit and creates a backup before changing the workspace.
The map reloads around the changed class. [warmly] Our new class now appears in the
tree, and its tooltip says Local Class.

[calm] Rejected proposals stay in the history too. [serious] If another edit has changed the
tree since a proposal was made, the old proposal cannot be applied silently.
It must be resubmitted against the current revision.

[thoughtful] This is a reviewed local change. It has not rewritten the published mapping
or the original KIF files, [short pause] and it has not been sent anywhere.

## SCENE 11: Move a subtree without losing the graph [budget: 45 seconds]

> **Shot:** drag `Residence` onto `Building` (disposable workspace). The preview shows target parent `Building`; `PostalPlace` retained; descendants `PermanentResidence`, `ResidentialBuilding`, `TemporaryResidence` attached; mapping evidence flagged. Then hold on the refused cycle (`SelfConnectedObject` → `AstronomicalBody`, frame fig11c).

[matter-of-fact] To prepare a move, drag one SUMO class onto another. The panel identifies the
target parent. [calm] The class's descendants stay attached, and its other parents
are retained.

> **NEW DRAFT line** (Claude, 2026-11-03; Tom chose an honest-experiment demo over a misleading "improvement"). For Codex and maintainer review.
> **Source:** Residence's documentation, *"A Building or part of a Building which provides some accomodation for sleeping"* (Merge.kif ~l.20367). `ApartmentUnit ⊂ SingleFamilyResidence ⊂ PermanentResidence ⊂ Residence` (MILO l.10335), and it never reaches `Building`.

[thoughtful] This move is an experiment, not a recommendation. SUMO defines a residence as a building, or part of one, so an apartment would no longer fit. [short pause] The preview is where a maintainer sees that.

The editor checks for cycles, including paths through secondary parents and
classes outside the visible map. It recalculates the displayed depths and
branch membership. A retained parent can become the displayed parent when it
provides a shorter path.

[serious] Existing mapping evidence may now need review. The editor flags affected
classes and descendants. [thoughtful] It keeps the published links visible as evidence;
it does not pretend that a tree move has reconciled them automatically.

## SCENE 12: Export a real KIF change [budget: 45 seconds]

> **Shot:** fig14 Download KIF changes, zip contents and removed/added subclass lines.

[calm] When the applied changes are ready for inspection, download the KIF changes.

[matter-of-fact] The zip contains a source patch, complete changed KIF files, and an audit
record. A move removes the old subclass assertion and adds the new one.
Documentation edits replace the relevant English documentation statement.

[calm] Before export, the editor reparses the result and checks that the actual
subclass assertions match the expected ones, including assertions outside
the visible map. The source patch is ready for human inspection and the
maintainers' normal validation. [serious] Downloading it does not publish it or alter
an upstream checkout.

## SCENE 13: The limits that keep the result honest [budget: 35 seconds]

> **Shot:** hold panel operation list; show upstream rename/delete refusal, then mapping warning.

[serious] This first release edits the five hundred classes in the mapped snapshot.
It is not a general editor for every KIF axiom. Upstream rename and delete
are refused because a name may occur in rules, instances and other statements
that need a wider audit.

Mapping newly added local classes is also a remaining integration step.
And the structural export check is not a proof of logical consistency.
[short pause] [thoughtful] Those limits are explicit, so a useful local edit cannot be mistaken for
an approved, fully validated ontology release.

## SCENE 13b: Seven kinds of link, and when to use each (NEW DRAFT) [budget: 85 seconds]

> **New narration** (Claude, 2026-11-03, at Tom's request: a narrative describing the link classes and when to assign them, placed before the close). In both cuts. **DRAFT for Codex and maintainer review.** Every example is a real link in the map; the sources are in the fact sheet below.

> **Shot:** the ribbon legend (fig02). Then, per label, focus on its example link: Island ↔ GB471 Islands; Vertebrate ↔ QL614 Fishes; the Sleep rows; Vertebrate ↔ QL671 Birds with its tooltip; Virus ↔ QR355 Virology.

[calm] Every link between the two trees carries one of seven labels, and each label has a rule.

[matter-of-fact] Exact means the same subject on both sides, like the SUMO class Island and the library's row for islands. It is rarer than you might expect.

Broader means strict containment: everything the library row shelves falls inside the SUMO class. Every fish in the fishes row is a vertebrate. [serious] One checked counterexample breaks the claim.

[matter-of-fact] Narrower is the mirror: every kind of the class must be shelved inside the row. Sleep fails that test. The library shelves it under psychology, physiology, medicine, and hygiene.

Partial means a real overlap, with neither side containing the other. The birds row also shelves birdhouses and bird feeders, which are not birds.

Generic marks the row that is the general home of the class, like virology for viruses. Related records a weaker association, and none records that no positive claim was made.

[thoughtful] Two rules keep the judging honest. Judge the subject, not the carrier: a book about fish is still about fish. [short pause] And the care of a thing is a different subject from the thing itself. Cat care is not a cat.

> **Fact sheet for Scene 13b** (not narrated):
>
> | Narrated claim | Source |
> |---|---|
> | seven labels | exact, broader, narrower, partial, generic, related, none: the ribbon legend (Scene 2) and `final_link.final_relation` |
> | Island ↔ islands, exact | `Island` ↔ `GB471-478.995` Islands, exact (depth 6) |
> | exact is rare | 8 exact links out of about 5,000 non-implied links at depths 5–6 (7 at depth 5, 1 at depth 6, 2026-11-03) |
> | broader = strict containment; one checked counterexample breaks it | Tom's rulings: broader = strict containment; **R9**, one mechanically checked counterexample suffices |
> | every fish is a vertebrate | `Vertebrate` ↔ `QL614-639.8` Fishes: broader, held on both seats (`containment:both seats hold`) |
> | narrower is the mirror; sleep fails | Mirror-R9. LC notes: BF1048-1108 *Cf. QP425+ Physiology of sleep*; RA773-788 *Cf. QP425+ Physiology of sleep; Cf. RC547+ Sleep disturbances*. Sleep is shelved in BF, QP, RC and RA, so no single row holds every kind |
> | birdhouses and bird feeders | QL671-699 Birds, LC note *"Including birdhouses, bird feeders, birdcall whistles, and gardening to attract birds"* (row L05800). `Vertebrate` ↔ that row is partial |
> | virology for viruses, generic | `Virus` ↔ `QR355-502` Virology, generic (Tom's ruling, 2026-11-03) |
> | subject, not carrier | **R10** |
> | care of a thing ≠ the thing; cat care is not a cat | **R12**. `Animal` ↔ `SF441-450` Cats: partial, both seats, counterexample *LC SF447: culture and care of cats* (batch d5i) |

## SCENE 14: Close [budget: 40 seconds]

> **Shot:** return to the overview; end card links to repository and user guide.

[warmly] Two trees, graded claims between them, and disagreements you can inspect.
[thoughtful] Now there is a path from a discovered problem to a reviewed local correction,
and from that correction to a concrete KIF change.

[calm] The library categories grew from books that needed shelves. The ontology
categories grew from distinctions needed for formal reasoning. [short pause] Where the two
agree, we have corroboration. [thoughtful] Where they disagree, we have a place to investigate.

[warmly] OntoloMerge preserves that evidence while letting people work on the structure.
The package includes the user guide, the editor and its validation tools.
[short pause] Thank you for watching.

---

## FINAL SLIDE: Tom's commissioned text card (wording preserved verbatim)

> Not included in the narration word count. On screen, show the card **without** tags. If it's voiced, paste the cued version below: same words, read slowly, one breath per line.

**On-screen text (verbatim, no tags):**

> Warrant from below, logic from above,
> and an audited, honest bridge in between —
> with the disagreements preserved, not smoothed over.
>
> The exacts are where the two systems redundantly agree;
> the partials are the surveyed boundary between meaning and logic.
> That boundary, measured, is the third thing neither system could be.

**Voiced version (paste into ElevenLabs):**

[long pause] [thoughtful] Warrant from below… logic from above…
and an audited, honest bridge in between —
[calm] with the disagreements preserved, not smoothed over.

[long pause] [thoughtful] The exacts are where the two systems redundantly agree;
the partials are the surveyed boundary between meaning and logic.
[short pause] [warmly] That boundary, measured… is the third thing neither system could be.

[long pause]

## Shorter edits (production notes)

- **SUMO Director's Cut: the primary video** (Tom, 2026-11-03: *"to educate ALL about SUMO"*). Its main audience is SUMO experts learning the editor.
  - **Boundaries** are marked in the scenes above with `> ✂ Director's Cut: IN / OUT`:

    | Scene | In the cut |
    |---|---|
    | 1 | all |
    | 1b | all (the SUMO primer, new draft) |
    | 2 | out |
    | 3 | holes, misfit classes and the counterexample tooltip (paragraphs 2–3) |
    | 4–6 | out |
    | 7 | the first two paragraphs |
    | 8–14 | all, including 13b (the link classes, new draft) |
    | Final Slide | in |

  - **Length:** about **1,100 narrated words ≈ 7.3 minutes at 150 wpm** (including the 87-word primer), measured, plus the demonstration holds. Budget **8–9 minutes**. The older "about five minutes" estimate was unmeasured.
  - **Why this order and not editor-first:** the cut keeps the evidence chain. A discovered problem (Scene 3) comes before the reviewed correction (8–11), the KIF change (12) and the limits (13). That answers an expert's first question: why is this edit warranted?
  - **Every IN boundary opens on `[calm]`,** so the voice never carries an emotion across a cut.
  - **Footage:** keep the ribbon legend visible in the Scene 3 shot, since Scene 2 is cut.
  - Retain the local-workspace distinction and the scope limits.
- **Full version (extended cut):** every scene. It's the mapping-tour edition, for LCC and knowledge-organization viewers.
- **Three-minute demonstration:** overview → add/preview → review/apply → KIF export → explicit limits. Show the written guide as the end card.
- Re-time after narration is recorded. Don't squeeze the Apply or export preview so tightly that the audience can't read what it approves.

## CREDITS CARD: after the final slide (not narrated; matches the Initial video, approved by Tom 2026-11-03)

**Tom Schaefer**: ideation and human advisor

**Kimi**: original viewer, layout, mapping workbench, package and editor plan  
**Claude**: mapping, reconciliation, source checks, viewer brief and narration cues  
**Grok**: mapping, independent adversarial checks and screen footage  
**GPT / Astra**: mapping and independent falsification  
**GPT / Codex**: SUMO editor, validation, package and guides/script

**SUMO maintainers and contributors**: ontology and documentation  
**Library of Congress**: classification outline and schedule material

> Hold long enough to read. These role credits are explicitly requested for this release; detailed per-link reviewer records remain excluded from the public data. See CREDITS.md and original source notices.
