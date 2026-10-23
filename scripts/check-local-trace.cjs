// Cross-check actual direct-VM transitions with the independent live-proof oracle.
const fs=require('node:fs');
const {initial,plan,replay,previewOracle,finalCheck}=require('./scenario.cjs');
const {id,accounts,trace}=JSON.parse(fs.readFileSync(0,'utf8'));
const revision='a'.repeat(40),items=plan(id);
const equal=(a,b)=>require('node:util').isDeepStrictEqual(a,b);
let previous=initial(id,revision,accounts);
if(trace.length!==items.length)throw Error('Incomplete local planned trace');
for(let i=0;i<items.length;i++){
 const item=items[i],actual=trace[i];
 if(!equal(actual.before,previous))throw Error('Local trace linkage');
 if(item.method==='advance'&&!equal(actual.preview,previewOracle(previous,id,item.args[0])))throw Error('Independent preview differs from direct VM');
 replay(previous,item,actual.after,id,revision,accounts);previous=actual.after;
}
finalCheck(previous,id);console.log('Independent oracle matches actual direct-VM scenario: '+id);
