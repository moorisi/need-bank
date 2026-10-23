const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),repo='moorisi/need-bank';
const cases={avoidance:{status:'COMPLETE',states:['DONE','DONE']},reuse:{status:'COMPLETE',states:['DONE','ABORTED']},review:{status:'REVIEW'},blocked:{status:'BLOCKED'}};
const resources=['processor-units','storage-units'];
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b)),clone=x=>JSON.parse(JSON.stringify(x));
function assert(ok,message){if(!ok)throw Error(message);}
function source(id){return JSON.parse(fs.readFileSync(path.join(root,'fixtures',id+'.json')));}
function observations(id){return JSON.parse(fs.readFileSync(path.join(root,'tests',id+'-expected.json')));}
function capacity(id){return id==='reuse'?[2,2]:[3,3];}
function descriptor(id,revision){return [{url:`https://raw.githubusercontent.com/${repo}/${revision}/fixtures/${id}.json`,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'fixtures',id+'.json'))).digest('hex')}];}
function args(id,revision,accounts){const d=descriptor(id,revision)[0],report=source(id);return [repo,id+'-pool',resources,capacity(id),accounts.slice(0,2),report.jobs.map(j=>j.job),report.jobs.map(j=>j.steps.map(s=>s.id)),d.url,d.sha256];}
function configuration(a){return {repository:a[0],pool:a[1],resources:a[2],capacity:a[3],participants:a[4],jobs:a[5],steps:a[6],url:a[7],sha256:a[8]};}
function initial(id,revision,accounts){return {configuration:configuration(args(id,revision,accounts)),assessment:null,compiled:null,ledger:{status:'WAITING',cursors:[0,0],allocations:[[0,0],[0,0]],states:['WAITING','WAITING'],free:capacity(id),safe_order:[]},events:[]};}
function compiledOracle(id){
 const rows=observations(id).jobs,unknown=rows.flatMap(j=>j.steps.filter(s=>s.operation==='UNKNOWN').map(s=>[j.job,s.id]));
 if(unknown.length)return {status:'REVIEW',reason:{kind:'UNKNOWN_STEPS',steps:unknown},programs:[]};
 const programs=[];
 for(const job of rows){
  const operations=job.steps.map(s=>({operation:s.operation,units:s.units}));
  const holdings=[[0,0],...operations.map((_,position)=>resources.map((_,r)=>operations.slice(0,position+1).reduce((total,s)=>total+(s.operation==='ACQUIRE'?1:-1)*s.units[r],0)))];
  for(let p=1;p<holdings.length;p++){
   const kind=holdings[p].some(x=>x<0)?'OVER_RELEASE':holdings[p].some((x,r)=>x>capacity(id)[r])?'OVER_CAPACITY':null;
   if(kind)return {status:'BLOCKED',reason:{kind,job:job.job,step:job.steps[p-1].id},programs:[]};
  }
  if(holdings.at(-1).some(x=>x!==0))return {status:'BLOCKED',reason:{kind:'UNRETURNED_UNITS',job:job.job},programs:[]};
  programs.push({job:job.job,operations,holdings,remaining_peaks:holdings.map((_,p)=>resources.map((_,r)=>Math.max(...holdings.slice(p).map(h=>h[r]))))});
 }
 return {status:'ACTIVE',reason:null,programs};
}
function permutations(xs){if(!xs.length)return [[]];return xs.flatMap((x,i)=>permutations(xs.filter((_,j)=>j!==i)).map(rest=>[x,...rest]));}
function orderOracle(programs,ledger){
 // Factorial independent oracle, unlike the contract's greedy safety algorithm.
 const jobs=ledger.states.flatMap((s,i)=>s==='RUNNING'?[i]:[]);
 for(const order of permutations(jobs)){
  const work=[...ledger.free];let valid=true;
  for(const i of order){const peak=programs[i].remaining_peaks[ledger.cursors[i]];if(peak.some((p,r)=>p-ledger.allocations[i][r]>work[r])){valid=false;break;}for(let r=0;r<work.length;r++)work[r]+=ledger.allocations[i][r];}
  if(valid)return order;
 }
 return null;
}
function compiledLedger(id){
 const result=initial(id,'a'.repeat(40),Array(4).fill('0x'+'1'.repeat(40))).ledger,compiled=compiledOracle(id);
 result.status=compiled.status;result.states=Array(2).fill(compiled.status==='ACTIVE'?'RUNNING':compiled.status);
 result.safe_order=compiled.status==='ACTIVE'?orderOracle(compiled.programs,result):[];
 return result;
}
function candidateOracle(programs,ledger,job){
 const operation=programs[job].operations[ledger.cursors[job]],sign=operation.operation==='ACQUIRE'?1:-1,delta=operation.units.map(x=>sign*x);
 if(delta.some((x,r)=>x>ledger.free[r]))return {verdict:'INSUFFICIENT',ledger:null};
 const next=clone(ledger);next.free=ledger.free.map((f,r)=>f-delta[r]);next.allocations[job]=ledger.allocations[job].map((a,r)=>a+delta[r]);next.cursors[job]++;
 if(next.cursors[job]===programs[job].operations.length)next.states[job]='DONE';
 const order=orderOracle(programs,next);if(order===null)return {verdict:'UNSAFE',ledger:null};
 next.safe_order=order;next.status=next.states.includes('RUNNING')?'ACTIVE':'COMPLETE';return {verdict:'ALLOWED',ledger:next};
}
function previewOracle(state,id,job){if(state.ledger.status!=='ACTIVE')return {verdict:'DISABLED',ledger:null};if(state.ledger.states[job]!=='RUNNING')return {verdict:'TERMINAL',ledger:null};return candidateOracle(compiledOracle(id).programs,state.ledger,job);}
function event(kind,job,sender,ledger,operation,units){return {kind,job,sender,cursor:job<0?-1:ledger.cursors[job],operation,units,free:ledger.free,safe_order:ledger.safe_order};}
function plan(id){
 if(id==='avoidance')return [
 {label:id+'-reject-before-compile',caller:0,method:'advance',args:[0],error:'[EXPECTED] Pool not active'},
 {label:id+'-compile',caller:2,method:'compile',args:[]},
 {label:id+'-reject-other-signer',caller:3,method:'advance',args:[0],error:'[EXPECTED] Only job participant'},
 {label:id+'-amber-borrow-processor',caller:0,method:'advance',args:[0]},
 {label:id+'-reject-free-but-unsafe',caller:1,method:'advance',args:[1],error:'[EXPECTED] Unsafe remaining claims'},
 {label:id+'-amber-borrow-storage',caller:0,method:'advance',args:[0]},
 {label:id+'-amber-return',caller:0,method:'advance',args:[0]},
 {label:id+'-bronze-borrow-storage',caller:1,method:'advance',args:[1]},
 {label:id+'-bronze-borrow-processor',caller:1,method:'advance',args:[1]},
 {label:id+'-bronze-return',caller:1,method:'advance',args:[1]},
 {label:id+'-reject-complete',caller:0,method:'advance',args:[0],error:'[EXPECTED] Pool not active'}
 ];
 if(id==='reuse')return [
 {label:id+'-compile',caller:2,method:'compile',args:[]},
 {label:id+'-amber-borrow-processor',caller:0,method:'advance',args:[0]},
 {label:id+'-reject-unavailable',caller:1,method:'advance',args:[1],error:'[EXPECTED] Insufficient free units'},
 {label:id+'-amber-return-processor',caller:0,method:'advance',args:[0]},
 {label:id+'-amber-borrow-storage',caller:0,method:'advance',args:[0]},
 {label:id+'-bronze-borrow-after-past-peak',caller:1,method:'advance',args:[1]},
 {label:id+'-reject-other-abort',caller:0,method:'abort',args:[1],error:'[EXPECTED] Only job participant'},
 {label:id+'-bronze-abort',caller:1,method:'abort',args:[1]},
 {label:id+'-amber-return-storage',caller:0,method:'advance',args:[0]},
 {label:id+'-reject-terminal',caller:1,method:'advance',args:[1],error:'[EXPECTED] Pool not active'}
 ];
 return [
 {label:id+'-compile',caller:2,method:'compile',args:[]},
 {label:id+'-reject-amber',caller:0,method:'advance',args:[0],error:'[EXPECTED] Pool not active'},
 {label:id+'-reject-bronze',caller:1,method:'advance',args:[1],error:'[EXPECTED] Pool not active'},
 {label:id+'-reject-abort',caller:0,method:'abort',args:[0],error:'[EXPECTED] Pool not active'},
 {label:id+'-reject-recompile',caller:3,method:'compile',args:[],error:'[EXPECTED] Runbook already compiled'}
 ];
}
function check(state,id,revision,accounts){
 assert(Object.keys(state).sort().join(',')==='assessment,compiled,configuration,events,ledger'&&equal(state.configuration,configuration(args(id,revision,accounts))),'Exact source-bound pool configuration');
 const ledger=state.ledger;assert(Object.keys(ledger).sort().join(',')==='allocations,cursors,free,safe_order,states,status'&&ledger.cursors.length===2&&ledger.allocations.length===2&&ledger.states.length===2&&ledger.free.length===2,'Exact bounded ledger');
 for(let r=0;r<2;r++)assert(Number.isInteger(ledger.free[r])&&ledger.free[r]>=0&&ledger.allocations.every(a=>a.length===2&&Number.isInteger(a[r])&&a[r]>=0)&&ledger.free[r]+ledger.allocations.reduce((total,a)=>total+a[r],0)===capacity(id)[r],'Resource conservation');
 if(state.assessment===null){assert(equal(state,initial(id,revision,accounts)),'No interpretation or grants before consensus');return;}
 const a=state.assessment,report=source(id),expected=observations(id);
 assert(Object.keys(a).sort().join(',')==='observations,source'&&equal(a.source,report)&&Object.keys(a.observations).join(',')==='jobs'&&a.observations.jobs.length===2,'Full fetched runbook and complete jobs');
 for(let j=0;j<2;j++){
  const job=a.observations.jobs[j],want=expected.jobs[j];
  assert(Object.keys(job).sort().join(',')==='job,steps'&&job.job===want.job&&job.steps.length===want.steps.length,'Exact ordered interpretation roster');
  for(let p=0;p<want.steps.length;p++){const s=job.steps[p];assert(Object.keys(s).sort().join(',')==='id,operation,quote,units'&&Object.keys(want.steps[p]).every(k=>equal(s[k],want.steps[p][k])),'Every independently expected operation and quantity');assert(typeof s.quote==='string'&&s.quote.length>=12&&s.quote.length<=400&&report.jobs[j].steps[p].text.includes(s.quote),'Source-linked material instruction quote');}
 }
 const compiled=compiledOracle(id);assert(equal(state.compiled,compiled),'Independent complete plan simulation and suffix-peak oracle');
 if(compiled.status!=='ACTIVE'){assert(equal(ledger,compiledLedger(id))&&state.events.length===1,'Disabled pool never grants or aborts');return;}
 for(let i=0;i<2;i++){
  const cursor=ledger.cursors[i],status=ledger.states[i],program=compiled.programs[i];
  assert(Number.isInteger(cursor)&&cursor>=0&&cursor<=program.operations.length&&['RUNNING','DONE','ABORTED'].includes(status),'Fixed program prefix and terminal state');
  assert(equal(ledger.allocations[i],status==='ABORTED'?[0,0]:program.holdings[cursor]),'Exact source-derived current holdings');
  if(status==='DONE')assert(cursor===program.operations.length,'Done only at final step');
  if(status==='RUNNING')assert(cursor<program.operations.length,'Unfinished program cursor');
 }
 assert(ledger.status===(ledger.states.includes('RUNNING')?'ACTIVE':'COMPLETE')&&equal(ledger.safe_order,orderOracle(compiled.programs,ledger)),'Independent safe completion witness');
}
function replay(before,item,after,id,revision,accounts){
 check(before,id,revision,accounts);check(after,id,revision,accounts);
 if(item.error){assert(equal(before,after),'Rejected call changed any state or event');return;}
 const e=clone(before),job=item.args[0],sender=accounts[item.caller];
 if(item.method==='compile'){
  assert(e.assessment===null,'One immutable runbook compilation');e.assessment=clone(after.assessment);e.compiled=compiledOracle(id);e.ledger=compiledLedger(id);
  e.events.push(event('COMPILE',-1,sender,e.ledger,e.compiled.status,[0,0]));
 }else{
  assert(e.ledger.status==='ACTIVE'&&e.ledger.states[job]==='RUNNING'&&sender===e.configuration.participants[job],'Only bound participant controls running job');
  if(item.method==='advance'){
   const operation=e.compiled.programs[job].operations[e.ledger.cursors[job]],candidate=candidateOracle(e.compiled.programs,e.ledger,job);assert(candidate.verdict==='ALLOWED','Only safe source operation admitted');e.ledger=candidate.ledger;e.events.push(event('ADVANCE',job,sender,e.ledger,operation.operation,operation.units));
  }else if(item.method==='abort'){
   const held=[...e.ledger.allocations[job]];e.ledger.free=e.ledger.free.map((f,r)=>f+held[r]);e.ledger.allocations[job]=[0,0];e.ledger.states[job]='ABORTED';e.ledger.safe_order=orderOracle(e.compiled.programs,e.ledger);e.ledger.status=e.ledger.states.includes('RUNNING')?'ACTIVE':'COMPLETE';e.events.push(event('ABORT',job,sender,e.ledger,'RELEASE',held));
  }else throw Error('Unknown signed operation');
 }
 assert(equal(e,after),'Independent full ledger and event replay: '+item.label);
}
function finalCheck(state,id){assert(state.ledger.status===cases[id].status,'Expected scenario status');if(cases[id].states)assert(equal(state.ledger.states,cases[id].states)&&equal(state.ledger.free,capacity(id)),'All units returned and exact terminal states');}
module.exports={cases,args,descriptor,initial,plan,replay,check,previewOracle,compiledOracle,orderOracle,candidateOracle,finalCheck};
