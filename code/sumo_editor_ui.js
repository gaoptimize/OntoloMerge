/* OntoloMerge SUMO editor UI, injected only by serve_sumo_editor.py.
 * modsource: ontolomerge_sumo_editor_v1_20261103
 * Public release.*/
const editorStyle = document.createElement("style");
editorStyle.textContent = `
 #editorOpen{background:#0e7490;color:white;border:1px solid #67e8f9;border-radius:4px;padding:4px 10px;cursor:pointer}
 #editorPanel{display:none;position:fixed;right:12px;top:95px;bottom:16px;width:min(470px,calc(100vw - 48px));background:#fff;border:1px solid #94a3b8;border-radius:8px;box-shadow:0 8px 40px #20303c55;z-index:15;overflow:auto;padding:16px;font-size:13px;color:#20303c}
 #editorPanel h2{margin:0;font-size:19px} #editorPanel h3{margin-bottom:6px}
 #editorPanel label{display:block;margin-top:9px;font-weight:600}
 #editorPanel input:not([type=checkbox]),#editorPanel select,#editorPanel textarea{box-sizing:border-box;width:100%;font:inherit;padding:6px;border:1px solid #94a3b8;border-radius:4px;background:white;color:#20303c}
 #editorPanel textarea{resize:vertical} #editorPanel button{padding:6px 10px;margin:5px 5px 0 0;cursor:pointer;border:1px solid #94a3b8;border-radius:4px;background:#f1f5f9;color:#20303c}
 #editorPanel button:disabled{opacity:.45;cursor:default} #editorPanel .primary{background:#0e7490;color:white}
 #editorPanel .muted{font-size:12px;color:#526575} #editorPanel .notice{padding:8px;background:#ecfeff;border-left:3px solid #0891b2;margin:10px 0}
 #editorPreview{white-space:pre-wrap;overflow-wrap:anywhere;background:#f8fafc;padding:9px;border:1px solid #cbd5e1;max-height:260px;overflow:auto}
 #editorError{color:#b91c1c;white-space:pre-wrap} #editorQueue article{border-top:1px solid #cbd5e1;padding:8px 0}
 #editorQueue .applied{color:#166534} #editorQueue .rejected{color:#64748b} #editorPanel a{color:#0e7490}
 .class-edit-marker{pointer-events:none}
`;
document.head.appendChild(editorStyle);
const editorButton = document.createElement("button");
editorButton.id = "editorOpen";
editorButton.textContent = "SUMO editor";
editorButton.style.display = "none";
document.getElementById("bar").appendChild(editorButton);
const editorPanel = document.createElement("aside");
editorPanel.id = "editorPanel";
editorPanel.setAttribute("aria-label", "SUMO editor");
editorPanel.innerHTML = `
 <button id="editorClose" style="float:right" aria-label="Close editor">✕</button>
 <h2>SUMO editor</h2><div id="editorRevision" class="muted"></div>
 <div class="notice">Changes stay in your local workspace. Propose → review → apply.
 The published mapping and original KIF stay intact.</div>
 <p class="muted">Right-click a SUMO class to edit it. Drag SUMO → SUMO to propose a move.
 Secondary parents stay attached when moving. Delete and rename are available for local leaves.</p>
 <label for="edSubject">Existing class</label><input id="edSubject" list="edClasses" autocomplete="off" placeholder="Select a SUMO class"><datalist id="edClasses"></datalist>
 <label for="edAction">Operation</label><select id="edAction">
 <option value="edit_doc">Edit documentation</option><option value="add">Add subclass</option>
 <option value="move">Move to another parent</option><option value="rename">Rename local leaf</option>
 <option value="delete">Delete local leaf</option></select>
 <div id="edNameWrap"><label for="edName">New class name</label><input id="edName" placeholder="NewClassName"></div>
 <div id="edParentWrap"><label for="edParent">Target parent</label><input id="edParent" list="edClasses" autocomplete="off"></div>
 <div id="edExtraWrap"><label for="edExtra">Secondary parents (comma separated, optional)</label><input id="edExtra" list="edClasses"></div>
 <div id="edDocWrap"><label for="edDoc">English documentation</label><textarea id="edDoc" rows="6"></textarea></div>
 <label for="edInitials">Your initials (2–4 letters)</label><input id="edInitials" maxlength="4" placeholder="TSC">
 <label for="edNote">Reason / evidence</label><textarea id="edNote" rows="2"></textarea>
 <button id="edPreview">Preview change</button><button id="edPropose" class="primary">Save proposal</button>
 <div id="editorError" role="status" aria-live="polite"></div>
 <pre id="editorPreview" style="display:none"></pre>
 <h3>Review queue & history</h3>
 <p class="muted">Apply revalidates the proposal, backs up the workspace, then refreshes the tree. Older proposals need to be resubmitted if the tree has changed.</p>
 <label style="font-weight:400"><input type="checkbox" id="edReviewed"> I have reviewed the preview and intend to apply it locally.</label>
 <button id="edRefresh">Refresh queue</button>
 <div id="editorQueue"></div>
 <h3>For SUMO maintainers</h3><a href="/api/sumo_delta.zip" id="edExport">Download KIF changes (.zip)</a>
 <p class="muted">Contains a unified source diff, complete changed KIF files and an audit log. Exports applied edits only.
 Subclass assertions are round-trip checked. Semantic consistency still requires SUMO validation.</p>
`;
document.body.appendChild(editorPanel);
const ed = id => document.getElementById(id);
let editorToken = "", classEdits = [], editorRevision = DATA.editor.revision, editorBusy = false;
let reviewedEdit = null;
for (const name of Object.keys(DATA.sumo_nodes).sort()) {
 const option = document.createElement("option"); option.value = name;
 ed("edClasses").appendChild(option);
}
try { ed("edInitials").value = localStorage.getItem("om_initials") || ""; } catch (_) {}
function editorError(message) { ed("editorError").textContent = message; }
async function editorRequest(path, body) {
 const response = await fetch(path, body === undefined ? {} : {
  method:"POST", headers:{"Content-Type":"application/json", "X-OntoloMerge-Token":editorToken},
  body:JSON.stringify(body)
 });
 const result = await response.json();
 if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
 return result;
}
function editorForm() {
 const action = ed("edAction").value;
 return {action, class_name:(action === "add" ? ed("edName").value : ed("edSubject").value).trim(),
  parent:ed("edParent").value.trim(), new_name:ed("edName").value.trim(), doc:ed("edDoc").value,
  extra_parents:ed("edExtra").value.split(",").map(s=>s.trim()).filter(Boolean),
  initials:ed("edInitials").value.trim().toUpperCase(), note:ed("edNote").value.trim()};
}
function editorFields() {
 const action = ed("edAction").value;
 ed("edNameWrap").style.display = ["add","rename"].includes(action) ? "" : "none";
 ed("edParentWrap").style.display = ["add","move"].includes(action) ? "" : "none";
 ed("edExtraWrap").style.display = action === "add" ? "" : "none";
 ed("edDocWrap").style.display = ["add","edit_doc"].includes(action) ? "" : "none";
 const node = DATA.sumo_nodes[ed("edSubject").value.trim()];
 if (action === "edit_doc") ed("edDoc").value = node ? node.doc : "";
 if (action === "add") { ed("edParent").value = ed("edSubject").value; ed("edDoc").value = ""; }
 ed("editorPreview").style.display = "none"; reviewedEdit = null; ed("edReviewed").checked = false;
 editorError("");
}
function openClassEditor(subject, action="edit_doc", parent="") {
 editorPanel.style.display = "block";
 if (subject) ed("edSubject").value = subject;
 ed("edAction").value = action;
 editorFields();
 if (parent) ed("edParent").value = parent;
 loadClassEdits();
}
function summaryText(s) {
 function describe(n) { return n ? `${n.label}\nParents: ${(n.parents||[]).join(", ") || "(root)"}\nDepth: ${n.depth}\nOrigin: ${n.origin}\nDocumentation: ${n.doc}` : "(absent)"; }
 return `${s.action}: ${s.class_name}\n\nBEFORE\n${describe(s.before)}\n\nAFTER\n${describe(s.after)}\n\n${s.changed_classes.length} classes changed; ${s.removed_classes.length} removed; ${s.mapping_links_to_review} mapping links need review.\n${s.warning}`;
}
async function editorRun(work) {
 if (editorBusy) return;
 editorBusy = true; editorError("");
 ed("edPreview").disabled = ed("edPropose").disabled = true;
 try { await work(); } catch (error) { editorError(error.message); }
 finally { editorBusy=false; ed("edPreview").disabled=ed("edPropose").disabled=false; }
}
ed("edPreview").addEventListener("click", () => editorRun(async () => {
 const result = await editorRequest("/api/preview_class_edit", editorForm());
 ed("editorPreview").textContent = summaryText(result.summary); ed("editorPreview").style.display = "block";
 reviewedEdit = null;
}));
ed("edPropose").addEventListener("click", () => editorRun(async () => {
 const proposal = editorForm();
 const result = await editorRequest("/api/propose_class_edit", proposal);
 try { localStorage.setItem("om_initials", proposal.initials); } catch (_) {}
 ed("editorPreview").textContent = `Saved proposal #${result.id}. Awaiting review.\n\n` + summaryText(result.summary);
 ed("editorPreview").style.display="block";
 await loadClassEdits();
}));
async function loadClassEdits() {
 try {
  const result = await editorRequest("/api/class_edits");
  const changed=JSON.stringify(classEdits)!==JSON.stringify(result.rows);
  classEdits = result.rows; editorRevision = result.revision;
  ed("editorRevision").textContent = `Workspace revision ${editorRevision} · ${DATA.editor.applied} applied changes in this view`;
  ed("editorQueue").innerHTML = classEdits.length ? classEdits.map(item => {
   const p = item.payload, pending=item.status === "provisional", stale=item.base_revision !== editorRevision;
   return `<article><b>#${item.id} ${esc(p.action)} · ${esc(p.class_name)}</b>
    <div class="${item.status}">${esc(item.status)}${pending && stale ? " · stale — reject and re-propose" : ""} · ${esc(p.initials)} · ${esc(item.created_utc)}</div>
    ${p.note ? `<div>${esc(p.note)}</div>` : ""}
    ${pending ? `<button data-edit-preview="${item.id}" ${stale ? "disabled" : ""}>Preview #${item.id}</button>
     <button data-edit-apply="${item.id}" class="primary" ${stale ? "disabled" : ""}>Apply locally</button>
     <button data-edit-reject="${item.id}">Reject</button>` : `<div class="muted">Reviewed by ${esc(item.decided_by || "")} · ${esc(item.decided_utc || "")}</div>`}</article>`;
  }).join("") : '<p class="muted">No class edits yet.</p>';
  if(changed)rebuild(true);
 } catch (error) { editorError(error.message); }
}
ed("editorQueue").addEventListener("click", event => editorRun(async () => {
 const button = event.target.closest("button"); if (!button) return;
 const id = +(button.dataset.editPreview || button.dataset.editApply || button.dataset.editReject);
 const item = classEdits.find(e=>e.id === id); if (!item) return;
 if (button.dataset.editPreview) {
  const result = await editorRequest("/api/preview_class_edit", item.payload);
  ed("editorPreview").textContent = `Proposal #${id}\n\n` + summaryText(result.summary);
  ed("editorPreview").style.display="block";
  reviewedEdit = id; ed("edReviewed").checked=false; return;
 }
 const decision = button.dataset.editApply ? "apply" : "reject";
 if (decision === "apply" && (reviewedEdit !== id || !ed("edReviewed").checked))
  throw new Error(`Preview proposal #${id}, then check the review box before applying.`);
 const result = await editorRequest("/api/decide_class_edit", {id, decision, revision:editorRevision, initials:ed("edInitials").value.trim()});
 if (decision === "apply") {
  try { sessionStorage.setItem("om_editor_focus", item.payload.new_name && item.payload.action === "rename" ? item.payload.new_name : item.payload.action === "delete" ? "Entity" : item.payload.class_name); } catch (_) {}
  location.reload();
 } else await loadClassEdits();
}));
ed("edAction").addEventListener("change", editorFields);
ed("edSubject").addEventListener("change", editorFields);
ed("edRefresh").addEventListener("click", loadClassEdits);
ed("editorClose").addEventListener("click", ()=>editorPanel.style.display="none");
editorButton.addEventListener("click", ()=>openClassEditor(state.focus && state.focus.side === "s" ? state.focus.id : ed("edSubject").value));
svg.addEventListener("contextmenu", event => {
 const g = event.target.closest("[data-nid]");
 if (g && g.dataset.side === "s" && editorToken) { event.preventDefault(); openClassEditor(g.dataset.nid); }
});
window.addEventListener("mouseup", event => {
 if (!editorToken || !linkDrag || !linkDrag.moved || linkDrag.side !== "s") return;
 const g = event.target.closest ? event.target.closest("[data-nid]") : null;
 if (!g || g.dataset.side !== "s" || g.dataset.nid === linkDrag.id) return;
 const subject = linkDrag.id; linkDrag=null;
 if (dragPath) { dragPath.remove(); dragPath=null; }
 openClassEditor(subject, "move", g.dataset.nid);
}, true);
const originalNodeTip = nodeTip;
nodeTip = function(side, id) {
 let text = originalNodeTip(side, id);
 if (side === "s") {
  const n=DATA.sumo_nodes[id];
  if (n.origin === "local") text += '<br><b style="color:#0e7490">LOCAL CLASS</b> · not upstream SUMO';
  if ((DATA.editor_stale_terms||[]).includes(id)) text += '<br><b style="color:#b45309">Edited class: mapping/hole evidence requires review</b>';
  text += '<br><span style="color:#64748b">Right-click to edit this class</span>';
 }
 return text;
};
const originalEditorRebuild = rebuild;
rebuild = function(...args) {
 originalEditorRebuild(...args);
 const pending=classEdits.filter(e=>e.status === "provisional");
 ed("stats").textContent += ` · ${pending.length} class edits pending · local rev ${DATA.editor.revision}`;
 for (const item of pending) {
  const p=item.payload, target=p.action === "add" ? p.parent : p.class_name;
  const group=Array.from(svg.querySelectorAll('[data-side="s"][data-nid]')).find(g=>g.dataset.nid === target);
  if (!group) continue;
  const hit=group.querySelector(".hit"), x=hit.getAttribute("cx"), y=hit.getAttribute("cy");
  const marker=document.createElementNS("http://www.w3.org/2000/svg","circle");
  marker.setAttribute("class","class-edit-marker"); marker.setAttribute("cx",x); marker.setAttribute("cy",y);
  marker.setAttribute("r","11"); marker.setAttribute("fill","none");
  marker.setAttribute("stroke",p.action === "delete" ? "#b91c1c" : p.action === "move" ? "#d97706" : "#0891b2");
  marker.setAttribute("stroke-width","2"); marker.setAttribute("stroke-dasharray","3 2");
  group.appendChild(marker);
 }
};
try { const focus=sessionStorage.getItem("om_editor_focus"); if (focus && DATA.sumo_nodes[focus]) { state.focus={side:"s",id:focus}; editorPanel.style.display="block"; ed("edSubject").value=focus; } sessionStorage.removeItem("om_editor_focus"); } catch (_) {}
editorFields();
fetch("/api/health").then(r=>r.json()).then(health=> {
 if (health.mode === "sumo_editor") { editorToken=health.token; editorButton.style.display=""; ed("wbBadge").style.display="inline-block"; loadClassEdits(); }
}).catch(error=>editorError(error.message));
