// Real Chromium smoke test, isolated browser profile, preview only (no workspace writes).
// modsource: ontolomerge_browser_path_fix_20261103
// Public release.
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const here=dirname(fileURLToPath(import.meta.url));
const base=process.argv.find(a=>a.startsWith('--base='))?.slice(7)||'http://127.0.0.1:41772';
const writeTest=process.argv.includes('--write-test');
const profile=await mkdtemp(join(tmpdir(),'ontolomerge-browser-'));
const chromeExecutable=process.env.CHROME_PATH ||
 (process.platform==='win32' && process.env.ProgramFiles
  ? join(process.env.ProgramFiles,'Google','Chrome','Application','chrome.exe') : 'google-chrome');
const chrome=spawn(chromeExecutable,[
 '--headless=new','--no-first-run','--no-default-browser-check',
 '--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'
],{windowsHide:true,stdio:'ignore'});
let socket;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
try {
 let port;
 for(let i=0;i<100;i++) {
  try {port=+(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;} catch {}
  await sleep(100);
 }
 assert(port,'Chrome did not start');
 const target=await (await fetch(`http://127.0.0.1:${port}/json/new?${base}/`,{method:'PUT'})).json();
 socket=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
 let next=0;
 const pending=new Map(),errors=[];
 socket.onmessage=e=>{
  const message=JSON.parse(e.data);
  if(message.id) {const cb=pending.get(message.id);pending.delete(message.id);message.error?cb.reject(message.error):cb.resolve(message.result);}
  if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text+': '+message.params.exceptionDetails.exception?.description);
 };
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++next;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});
 const run=async expression=>{
  const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
 };
 await send('Runtime.enable');
 await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1600,height:1000,deviceScaleFactor:1,mobile:false});
 let ready=false;
 for(let i=0;i<100;i++) {
  ready=await run(`typeof editorToken !== 'undefined' && !!editorToken && !!document.querySelector('#svg text')`);
  if(ready)break;
  await sleep(150);
 }
 assert(ready,'editor did not initialize: '+errors.join('\n'));
 const baseline=await run(`({stats:document.getElementById('stats').textContent, pending:classEdits.length, revision:DATA.editor.revision})`);
 await run(`document.getElementById('editorOpen').click(); true`);
 assert.equal(await run(`document.getElementById('editorPanel').style.display`),'block');
 await run(`
  document.getElementById('edSubject').value='IntentionalProcess';
  document.getElementById('edAction').value='add';
  document.getElementById('edAction').dispatchEvent(new Event('change'));
  document.getElementById('edName').value='EditorBrowserCheck';
  document.getElementById('edDoc').value='A temporary browser preview; never saved.';
  document.getElementById('edInitials').value='TST';
  document.getElementById('edPreview').click(); true;
 `);
 let preview='';
 for(let i=0;i<100;i++) {
  preview=await run(`document.getElementById('editorPreview').textContent`);
  if(preview.includes('AFTER'))break;
  await sleep(100);
 }
 assert(preview.includes('EditorBrowserCheck'),'add preview failed: '+await run(`document.getElementById('editorError').textContent`));
 assert(preview.includes('1 classes changed'),'unexpected derived tree drift: '+preview);
 const png=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 await writeFile(join(here,'editor_browser_preview.png'),Buffer.from(png.data,'base64'));
 // Existing class right-click must open documentation, and SUMO->SUMO drag
 // uses capture-phase interception so the old link handler cannot consume it.
 await run(`document.getElementById('editorClose').click(); document.querySelector('[data-side="s"][data-nid="IntentionalProcess"]').dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true})); true;`);
 assert.equal(await run(`document.getElementById('edAction').value`),'edit_doc');
 assert.equal(await run(`document.getElementById('edSubject').value`),'IntentionalProcess');
 await run(`
  linkDrag={side:'s',id:'IntentionalProcess',moved:true};
  document.querySelector('[data-side="s"][data-nid="Process"]').dispatchEvent(new MouseEvent('mouseup',{bubbles:true})); true;
 `);
 assert.equal(await run(`document.getElementById('edAction').value`),'move');
 assert.equal(await run(`document.getElementById('edParent').value`),'Process');
 const unchanged=await run(`({pending:classEdits.length, revision:DATA.editor.revision})`);
 assert.deepEqual(unchanged,{pending:baseline.pending,revision:baseline.revision});
 if(writeTest) {
  await run(`
   openClassEditor('IntentionalProcess','add');
   ed('edName').value='EditorBrowserCheck'; ed('edDoc').value='Browser fixture class.'; ed('edInitials').value='TST';
   ed('edPropose').click(); true;
  `);
  for(let i=0;i<100;i++) {
   if(await run(`classEdits.some(e=>e.payload.class_name === 'EditorBrowserCheck')`))break;
   await sleep(100);
  }
  const proposalId=await run(`classEdits.find(e=>e.payload.class_name === 'EditorBrowserCheck')?.id`);
  assert(proposalId,'proposal was not saved');
  assert(await run(`!!document.querySelector('.class-edit-marker')`),'pending overlay missing');
  await run(`document.querySelector('[data-edit-preview="${proposalId}"]').click();true;`);
  for(let i=0;i<100;i++) {if(await run(`reviewedEdit === ${proposalId}`))break;await sleep(100);}
  assert.equal(await run(`reviewedEdit`),proposalId);
  await run(`ed('edReviewed').checked=true; document.querySelector('[data-edit-apply="${proposalId}"]').click();true;`);
  let applied=false;
  for(let i=0;i<100;i++) {
   try {applied=await run(`typeof DATA !== 'undefined' && !!DATA.sumo_nodes.EditorBrowserCheck && DATA.editor.revision === ${baseline.revision+1}`);} catch {}
   if(applied)break;
   await sleep(100);
  }
  assert(applied,'apply did not reload the tree');
  assert.equal(await run(`DATA.sumo_nodes.EditorBrowserCheck.origin`),'local');
  assert(await run(`!!document.querySelector('[data-nid="EditorBrowserCheck"]')`),'new class not rendered after apply');
  const exportResult=await fetch(`${base}/api/sumo_delta.zip`);
  assert.equal(exportResult.status,200);
  assert.equal(exportResult.headers.get('content-type'),'application/zip');
 }
 assert.deepEqual(errors,[]);
 const report={modsource:'ontolomerge_sumo_editor_v1_20261103',status:'PASS',baseline,writeTest,
  checks:['real Chromium boot','editor panel','add preview with exactly one changed class','right-click documentation','SUMO to SUMO move gesture','no JavaScript exceptions',writeTest?'disposable workspace: save, ring overlay, review, apply, reload, export':'no workspace writes']};
 await writeFile(join(here,'editor_browser_results.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));
} finally {
 if(socket)socket.close();
 chrome.kill();
}
