// Boot-test harness for the OntoloMerge artifact: stub the DOM, eval the
// inline script, assert the render pipeline completes end to end.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const m = html.match(/<script>([\s\S]*)<\/script>/);
if (!m) { console.error("FAIL: no inline script"); process.exit(1); }

const measureStub = { measureText: s => ({ width: String(s).length * 5.8 }) };
const ctxStub = new Proxy(measureStub, { get: (t, k) => (k in t ? t[k] : () => {}) });

function mkEl(id) {
  return {
    id, style: {}, dataset: {}, children: [],
    innerHTML: "", textContent: "", value: "", checked: false,
    getContext: () => ctxStub,
    appendChild(c) { this.children.push(c); if (!this.value && c.value) this.value = c.value; },
    addEventListener() {}, setAttribute() {}, getBoundingClientRect() {
      return { left: 0, top: 0, width: 1600, height: 900 };
    },
    closest() { return null; },
  };
}
const els = {};
const documentStub = {
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: tag => mkEl(tag),
  addEventListener() {},
};
globalThis.document = documentStub;
globalThis.window = { addEventListener() {} };
globalThis.localStorage = { getItem: () => null, setItem: () => {} };
globalThis.fetch = () => Promise.reject(new Error("no fetch in stub"));
// canvas for measureCtx
els.measure = mkEl("measure");
documentStub.createElement = tag => mkEl(tag);

let src = m[1].replace("const DATA =", "globalThis.DATA =");
try {
  eval(src);
} catch (e) {
  console.error("FAIL: script threw:", e.message);
  process.exit(1);
}

const svg = els.svg;
if (!svg || !svg.innerHTML) { console.error("FAIL: svg never rendered"); process.exit(1); }
const stats = els.stats && els.stats.textContent || "";
if (!/SUMO \d+ · LCC \d+ · links \d+ · crossings \d+ → \d+/.test(stats)) {
  console.error("FAIL: stats line wrong:", JSON.stringify(stats)); process.exit(1);
}
const nodeDots = (svg.innerHTML.match(/class="node"/g) || []).length;
if (nodeDots !== 0) { console.error("FAIL: node dots present:", nodeDots); process.exit(1); }
const treeEdges = (svg.innerHTML.match(/class="tree-edge"/g) || []).length;
if (treeEdges === 0) { console.error("FAIL: no tree edges"); process.exit(1); }
// no-line-zone: one occlusion mask per label, painted after hierarchy edges
// and before links, so no hierarchy line strikes through text.
const masks = (svg.innerHTML.match(/class="lblmask"/g) || []).length;
const labels = (svg.innerHTML.match(/<text class="(?:sumo|lcc)-lbl"/g) || []).length;
if (masks !== labels || masks === 0) {
  console.error("FAIL: label masks", masks, "!= labels", labels); process.exit(1);
}
const h = svg.innerHTML;
const iEdge = h.indexOf('class="tree-edge"'), iMask = h.indexOf('class="lblmask"'),
      iLink = h.indexOf("data-li="), iText = h.indexOf('<text class="sumo-lbl"');
if (!(iEdge > -1 && iEdge < iMask && iMask < iLink && iLink < iText)) {
  console.error("FAIL: paint order must be edges < masks < links < labels"); process.exit(1);
}
// riser/dot invariant (Tom's nit, 2026-11-03): a vertical riser may never
// land inside the dot zone (label end + 6, r=2.4) of a label to its left
// within its row span. Risers live in the per-depth channel anchored past
// the widest label's dot, so this must hold by construction.
const edges = [...h.matchAll(/class="tree-edge" d="M([\d.]+) ([\d.]+)H([\d.]+)V([\d.]+)H([\d.]+)"/g)]
  .map(g => ({ y1: +g[2], mx: +g[3], y2: +g[4] }));
const un = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const lbls = [...h.matchAll(/<text class="(?:sumo|lcc)-lbl" x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]*)<\/text>/g)]
  .map(g => ({ x: +g[1], y: +g[2] - 3, w: un(g[3]).length * 5.8 }));
let riserBad = 0;
for (const e of edges) {
  const yA = Math.min(e.y1, e.y2), yB = Math.max(e.y1, e.y2);
  for (const L of lbls) {
    if (L.x < e.mx - 0.5 && L.y > yA + 0.5 && L.y < yB - 0.5 &&
        e.mx < L.x + L.w + 6 + 2.4 - 0.01) riserBad++;
  }
}
if (riserBad > 0) {
  console.error("FAIL: risers inside label dot zones:", riserBad); process.exit(1);
}
// branch dropdown counts must describe the depth on screen (default ≤5):
// the selected branch's option links count equals the stats line's, and the
// option names the depth its counts are for.
const optSel = els.branch.children.find(o => o.value === els.branch.value) ||
               els.branch.children[0];
const optTxt = optSel ? optSel.textContent : "";
const grabLinks = s => { const m = /links (\d+)/.exec(s); return m ? +m[1] : null; };
if (grabLinks(optTxt) === null || grabLinks(optTxt) !== grabLinks(stats)) {
  console.error("FAIL: branch option links", grabLinks(optTxt),
                "!= stats links", grabLinks(stats), "-", JSON.stringify(optTxt));
  process.exit(1);
}
if (!/counts at depth ≤5/.test(optTxt)) {
  console.error("FAIL: branch option does not name its depth:", JSON.stringify(optTxt));
  process.exit(1);
}
console.log("stats:", stats);
console.log("tree edges:", treeEdges, "| node dots:", nodeDots);
console.log("PASS");
