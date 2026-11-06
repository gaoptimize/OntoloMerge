/* modsource: codex_ontolomerge_v04_20261105
 * Public release.
 * Included inline in v0.4 exports; catalog is read-only, edits remain proposals.
 */
if (DATA.catalog) {
  const catalog=DATA.catalog, allNodes=DATA.sumo_nodes;
  let graphScope='all', fileScope='';
  const style=document.createElement('style');
  style.textContent='#fileScope{max-width:260px}#branch{max-width:min(680px,70vw)}#catalogPanel{display:none;position:fixed;inset:12% 8%;z-index:20;background:#fff;border:1px solid #789;box-shadow:0 8px 50px #0005;padding:16px;overflow:auto;color:#20303c}#catalogPanel pre{white-space:pre-wrap;overflow-wrap:anywhere}#catalogPanel button{margin:4px}#catalogSummary{font-size:11px}';
  document.head.appendChild(style);
  const controls=document.createElement('span');
  controls.innerHTML='<label>graph <select id="graphScope"><option value="all">All KIF files</option><option value="root">Root modules</option><option value="merge">Merge foundation</option></select></label> <label>file <select id="fileScope"><option value="">All selected files</option></select></label> <button id="catalogOpen">Sources &amp; instances</button> <span id="catalogSummary"></span>';
  document.getElementById('bar').insertBefore(controls,branchSel.parentElement);
  const fileSelect=document.getElementById('fileScope');
  for(const f of catalog.files){const o=document.createElement('option');o.value=f.path;o.textContent=f.path;fileSelect.appendChild(o);}
  const panel=document.createElement('section');panel.id='catalogPanel';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','KIF source catalog');
  panel.innerHTML='<button id="catalogClose">Close</button><h2>KIF source catalog</h2><p>All sources are preserved. Experimental/test assertions are included when “All KIF files” is selected. New structure has not been assessed for LCC mapping.</p><label>Find a symbol or phrase <input id="catalogQuery"></label> <button id="catalogFind">Find assertions</button> <button id="catalogPrev">Previous page</button> <button id="catalogNext">Next page</button><div id="catalogContent"></div>';
  document.body.appendChild(panel);
  let catalogOffset=0;
  const output=document.getElementById('catalogContent');
  async function showCatalog(reset=true){
    if(reset)catalogOffset=0;
    panel.style.display='block';
    const file=fileSelect.value, q=document.getElementById('catalogQuery').value.trim();
    const files=catalog.files.filter(f=>!file||f.path===file);
    output.textContent='';
    const summary=document.createElement('p');summary.textContent=`${files.length} source files · ${files.reduce((s,f)=>s+f.forms,0).toLocaleString()} assertions · ${catalog.unreachable.length} classes outside Entity’s reachable graph. Source revision ${catalog.commit.slice(0,7)}.`;output.appendChild(summary);
    for(const f of files.slice(0,150)){const row=document.createElement('div');row.textContent=`${f.path}: ${f.forms.toLocaleString()} forms; ${f.role}; SHA-256 ${f.sha256}`;output.appendChild(row);}
    const disconnected=document.createElement('p');disconnected.textContent='Disconnected classes: '+catalog.unreachable.map(n=>n.name).join(', ');output.appendChild(disconnected);
    if(q && catalog.instances[q]){const p=document.createElement('p');p.textContent=`${q}: ${catalog.instances[q].count.toLocaleString()} named instance assertions; examples: ${catalog.instances[q].examples.join(', ')}`;output.appendChild(p);}
    if(location.protocol==='file:'){
      const note=document.createElement('p');note.textContent='For the complete assertion text and paged search, open this release through Start-SumoEditor.cmd. The static viewer includes file provenance and instance counts.';output.appendChild(note);return;
    }
    try{
      const r=await fetch('/api/catalog?'+new URLSearchParams({file,q,offset:String(catalogOffset)}));
      if(!r.ok)throw Error('Catalog service unavailable; restart the current editor.');
      const data=await r.json();
      const heading=document.createElement('p');heading.textContent=`Assertions ${catalogOffset+1}–${catalogOffset+data.rows.length} of ${data.total.toLocaleString()}`;output.appendChild(heading);
      for(const a of data.rows){const pre=document.createElement('pre');pre.textContent=`${a.file}:${a.line}\n${a.text}`;output.appendChild(pre);}
      document.getElementById('catalogPrev').disabled=catalogOffset===0;
      document.getElementById('catalogNext').disabled=catalogOffset+data.rows.length>=data.total;
    }catch(e){const p=document.createElement('p');p.textContent=e.message;output.appendChild(p);}
  }
  document.getElementById('catalogOpen').onclick=()=>showCatalog();
  document.getElementById('catalogClose').onclick=()=>panel.style.display='none';
  document.getElementById('catalogFind').onclick=()=>showCatalog();
  document.getElementById('catalogPrev').onclick=()=>{catalogOffset=Math.max(0,catalogOffset-25);showCatalog(false);};
  document.getElementById('catalogNext').onclick=()=>{catalogOffset+=25;showCatalog(false);};
  document.getElementById('catalogQuery').onkeydown=e=>{if(e.key==='Enter')showCatalog();};
  function selectedFiles(){return new Set(catalog.files.filter(f=>graphScope==='all'||graphScope==='root'&&!f.path.includes('/')||graphScope==='merge'&&f.path==='Merge.kif').map(f=>f.path));}
  function applyGraphScope(){
    const selected=selectedFiles(), parents=new Map();
    for(const [file,edges]of Object.entries(catalog.edges))if(selected.has(file))for(const [c,p]of edges){if(!parents.has(c))parents.set(c,new Set());parents.get(c).add(p);}
    // Local proposed/applied edits are an overlay. Canonical graph profiles do
    // not overwrite local parent changes or change published mapping decisions.
    for(const [t,n]of Object.entries(allNodes)){
      const canonical=catalog.original_parents[t];
      if(n.origin==='local'||canonical&&JSON.stringify([...n.parents].sort())!==JSON.stringify([...canonical].sort()))parents.set(t,new Set(n.parents));
    }
    const kids=new Map();for(const [c,ps]of parents)for(const p of ps){if(!kids.has(p))kids.set(p,[]);kids.get(p).push(c);}
    const depths=new Map([['Entity',0]]),queue=['Entity'];
    for(let i=0;i<queue.length;i++)for(const c of kids.get(queue[i])||[])if(!depths.has(c)){depths.set(c,depths.get(queue[i])+1);queue.push(c);}
    const nodes={}, bs=new Map();
    for(const t of queue){if(!allNodes[t])continue;const d=depths.get(t),ps=[...(parents.get(t)||[])].filter(p=>depths.has(p)&&allNodes[p]).sort();const shortest=ps.filter(p=>depths.get(p)===d-1);const branches=new Set(d===3?[t]:[]);if(d>3)for(const p of shortest)for(const b of bs.get(p)||[])branches.add(b);bs.set(t,branches);nodes[t]={...allNodes[t],depth:d,parents:ps,sp_parent:shortest.includes(allNodes[t].sp_parent)?allNodes[t].sp_parent:shortest[0]||null,branches:[...branches].sort()};}
    DATA.sumo_nodes=nodes;
    for(const k of Object.keys(sumoKids))delete sumoKids[k];
    for(const [t,n]of Object.entries(nodes))if(n.sp_parent)(sumoKids[n.sp_parent]||=[]).push(t);
    const stat=new Map();for(const [t,n]of Object.entries(nodes))for(const b of n.branches){if(!stat.has(b))stat.set(b,{name:b,sumo:0,links:0,lcc:new Set(),holes:0});stat.get(b).sumo++;}
    for(const lk of DATA.links)for(const b of nodes[lk.s]?.branches||[]){const s=stat.get(b);s.links++;s.lcc.add(lk.l);}
    DATA.branches=[...stat.values()].map(s=>({...s,lcc:s.lcc.size})).sort((a,b)=>b.links-a.links||a.name.localeCompare(b.name));
    const old=state.branch;branchSel.replaceChildren();for(const b of DATA.branches){const o=document.createElement('option');o.value=b.name;branchSel.appendChild(o);}
    branchSel.value=DATA.branches.some(b=>b.name===old)?old:DATA.branches[0]?.name;
    state.branch=branchSel.value;state.focus=null;
    document.getElementById('catalogSummary').textContent=`${selected.size} files · ${Object.keys(nodes).length.toLocaleString()} reachable classes`;
    refreshBranchOptions();rebuild();
  }
  const oldBuildVisible=buildVisible;
  buildVisible=function(){
    const v=oldBuildVisible();
    v.sumoIds=new Set([...v.sumoIds].filter(t=>DATA.sumo_nodes[t]));
    // A profile may omit some classes that retain published mapping evidence.
    v.links=v.links.filter(lk=>DATA.sumo_nodes[lk.s]&&DATA.lcc_nodes[lk.l]);
    if(!fileScope)return v;
    const eligible=new Set([...v.sumoIds].filter(t=>(allNodes[t]?.source_files||[]).includes(fileScope)));
    v.links=v.links.filter(lk=>eligible.has(lk.s));
    for(const t of [...eligible]){let p=DATA.sumo_nodes[t]?.sp_parent;while(p&&!eligible.has(p)){eligible.add(p);p=DATA.sumo_nodes[p]?.sp_parent;}}
    v.sumoIds=eligible;
    const lcc=new Set();for(const lk of v.links){let p=lk.l;while(p&&!lcc.has(p)){lcc.add(p);p=DATA.lcc_nodes[p]?.parent;}}v.lccIds=lcc;return v;
  };
  document.getElementById('graphScope').onchange=e=>{graphScope=e.target.value;fileScope='';fileSelect.value='';applyGraphScope();};
  fileSelect.onchange=()=>{
    fileScope=fileSelect.value;state.focus=null;
    if(fileScope){const term=Object.keys(DATA.sumo_nodes).find(t=>(allNodes[t].source_files||[]).includes(fileScope)&&DATA.sumo_nodes[t].branches.length);if(term){state.branch=DATA.sumo_nodes[term].branches[0];branchSel.value=state.branch;}}
    refreshBranchOptions();rebuild();
  };
  const originalCounts=branchCounts;
  branchCounts=function(name){if(!fileScope)return originalCounts(name);const terms=new Set(Object.entries(DATA.sumo_nodes).filter(([t,n])=>n.branches.includes(name)&&n.depth<=state.maxDepth&&(allNodes[t].source_files||[]).includes(fileScope)).map(([t])=>t));const links=DATA.links.filter(l=>terms.has(l.s));return {sumo:terms.size,links:links.length,lcc:new Set(links.map(l=>l.l)).size};};
  const oldTip=nodeTip;
  nodeTip=function(side,id){let h=oldTip(side,id);if(side==='s'){const n=DATA.sumo_nodes[id];h+=`<br><b>Sources:</b> ${esc((n.source_files||[]).join(', '))}`;if(n.mapping_depth!==undefined)h+=`<br>Original mapping depth: ${n.mapping_depth}`;if(catalog.instances[id])h+=`<br>Named instance assertions: ${catalog.instances[id].count.toLocaleString()}`;}return h;};
  // Store catalog navigation hooks for reproducible UI tests and accessibility.
  window.ontoloCatalog={applyGraphScope,showCatalog};
  document.getElementById('catalogSummary').textContent=`${catalog.files.length} files · ${Object.keys(allNodes).length.toLocaleString()} reachable classes`;
}
