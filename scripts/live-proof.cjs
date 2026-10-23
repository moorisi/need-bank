const fs=require('node:fs'),path=require('node:path');
const {root,assert,equal,digest,sourceHash,save,invoke,read,rpc,receipt}=require('./transport.cjs');
const {cases,args,descriptor,initial,plan,replay,previewOracle,finalCheck}=require('./scenario.cjs');
async function main(){
 assert(await rpc('eth_chainId',[])==='0xf22f','Gasless StudioNet only');
 const actors=JSON.parse(process.env.NEED_ACCOUNTS||'null');assert(actors?.length===4,'Two participants and two independent proof callers');
 const accounts=actors.map(a=>a.address.toLowerCase()),revision=fs.readFileSync(path.join(root,'config/fixture-revision.txt'),'utf8').trim();assert(/^[a-f0-9]{40}$/.test(revision),'Pinned fixture revision');
 const suite=[];
 const selected=process.env.NEED_SCENARIO||'all';assert(selected==='all'||Object.hasOwn(cases,selected),'Unknown proof scenario');
 for(const id of selected==='all'?Object.keys(cases):[selected]){
  const a=args(id,revision,accounts);
  for(const document of descriptor(id,revision)){const web=await fetch(document.url,{signal:AbortSignal.timeout(45000)});assert(web.ok&&digest(Buffer.from(await web.arrayBuffer()))===document.sha256,'Exact public snapshot report');}
  process.env.NEED_ACCOUNT=actors[0].name;
  const deployment=await invoke(id+'-deployment',['deploy','--contract','contracts/need_bank.py','--args',...a.map(v=>typeof v==='string'?v:JSON.stringify(v))]);
  const r=await receipt(id+'-deployment',deployment,true),contract=r.to_address||r.recipient;
  const d={id,args:a,contract,deployment,accounts,fixture_revision:revision,source_sha256:sourceHash,network:'studionet',chain_id:61999};suite.push(d);save('suite',suite);
  assert(fs.readFileSync(path.join(root,'contracts/need_bank.py')).equals(Buffer.from(await rpc('gen_getContractCode',[contract]),'base64')),'Exact live source');
  let state=await read(id+'-initial',['call',contract,'get_state']);assert(equal(state,initial(id,revision,accounts)),'Initial fixed resource bank');save(id+'-initial-state',state);
  const trace=[];
  for(const item of plan(id,accounts,revision)){
   process.env.NEED_ACCOUNT=actors[item.caller].name;const before=state;let preview;
   if(item.method==='advance'){preview=await read(item.label+'-preview',['call',contract,'preview','--args',String(item.args[0])]);assert(equal(preview,previewOracle(before,id,item.args[0])),'Independent admission preview');}
   const transaction=await invoke(item.label,['write',contract,item.method,...(item.args.length?['--args',...item.args.map(v=>typeof v==='string'?v:JSON.stringify(v))]:[])]);
   const rr=await receipt(item.label,transaction,!item.error);assert((rr.from_address||rr.sender).toLowerCase()===accounts[item.caller],'Actual participant signature');
   state=await read(item.label+'-state',['call',contract,'get_state']);replay(before,item,state,id,revision,accounts);
   if(item.error){const raw=Buffer.from(rr.consensus_data.leader_receipt[0].result,'base64');assert(raw[0]===1&&raw.subarray(1).toString('utf8')===item.error,'Exact expected rejection bytes');}
   trace.push({...item,transaction,state_before:before,state,...(preview?{preview}:{} )});save(id+'-trace',trace);console.log('VERIFIED',item.label,JSON.stringify({ledger:state.ledger,event_count:state.events.length}));
  }
  finalCheck(state,id);save(id+'-final-state',state);
 }
}
main().catch(e=>{console.error(e.stack,e.cause?.message||'');process.exitCode=1;});
