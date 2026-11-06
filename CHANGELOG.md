# Release notes

## 0.4 — complete-source exploration and column navigation

- Catalog all 145 pinned KIF files, preserving source bytes, file hashes and lines.
- Browse 10,415 reachable classes; retain 47 disconnected classes in the catalog.
- Select all files, root modules or Merge; filter by file and isolate subtrees.
- Step by measured column boundaries with arrow keys or buttons, without graph
  rebuilds between steps. Navigation remains anchored after manual pan/zoom.
- Replace quadratic crossing comparisons with exact inversion counting.
- Preserve 5,295 existing mapping links; distinguish original mapping depths.
- Recover SubjectiveStrongPositiveAttribute and SubjectiveStrongNegativeAttribute,
  whose multiline subclass assertions were omitted by the initial extractor.
- Keep newly imported classes unassessed unless an existing mapping is recorded.
- Offer read-only source search and instance summaries through the local server.

This is expanded ontology coverage, not a claim that every imported class has an
LCC mapping. Experimental/test sources remain explicitly labeled. The Initial
release and its download assets are retained for reproducibility.
