// Run from any directory: node research/scripts/check-threshold-planner.cjs
// Pure solver checks; this does not substitute for browser or live-game verification.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { solve, maximize, knownCost } = require('../../src/threshold-planner.js');
const root = path.resolve(__dirname, '../..');
const badge = (name, tiers) => ({ name, tiers });
const small = (badges, targets, extra={}) => solve({attrs:['A','B'],caps:{A:99,B:99},badges,targets,...extra});
const and = badge('Both', [[[['A',30],['B',35]]]]);
assert.deepEqual(small([and],{Both:1}).ratings,{A:30,B:35});
// Greedy would pick A30 for Either, then also raise B. The global optimum shares B31.
const either = badge('Either', [[[['A',30]],[['B',31]]]]);
const second = badge('Second', [[[['B',31]]]]);
assert.deepEqual(small([either,second],{Either:1,Second:1}).ratings,{A:25,B:31});
assert.deepEqual(small([either],{Either:1},{floors:{B:40}}).ratings,{A:25,B:40});
assert.equal(small([and],{Both:1},{caps:{A:29,B:99}}).ok,false);
assert.equal(small([],{},{floors:{A:80},caps:{A:79,B:99}}).errors[0].type,'floor');
assert.throws(()=>small([],{},{floors:{A:null}}),/Invalid minimum/);
assert.deepEqual(small([],{}).ratings,{A:25,B:25});
assert.equal(small([and],{Both:1},{ceilings:{A:29}}).ok,false);
assert.deepEqual(small([either],{Either:1},{ceilings:{A:29}}).ratings,{A:25,B:31});
assert.equal(small([],{},{floors:{A:70},ceilings:{A:69}}).errors[0].type,'ceiling');
assert.throws(()=>small([],{},{ceilings:{A:null}}),/Invalid maximum/);
assert.throws(()=>small([],{},{ceilings:{A:100}}),/Invalid maximum/);
assert.throws(()=>small([],{},{ceilings:{A:70.5}}),/Invalid maximum/);
assert.deepEqual(small([],{},{floors:{A:70},ceilings:{A:70}}).ratings,{A:70,B:25});
// The existing tier evaluator requires every preceding tier, even for non-nested input.
const prefix=badge('Prefix',[[[['A',30]]],[[['B',35]]]]);
assert.deepEqual(small([prefix],{Prefix:2}).ratings,{A:30,B:35});
const dunk=badge('Dunk',[[[['DUNK',80]]]]);
for(const mode of ['DD','SD','max']){
  const result=solve({attrs:['DD','SD'],caps:{DD:75,SD:85},badges:[dunk],targets:{Dunk:1},dunkMode:mode});
  assert.equal(result.ok,mode!=='DD');
  if(result.ok)assert.deepEqual(result.ratings,{DD:25,SD:80});
}
console.log('AND/OR choices, shared ratings, floors, blocked caps, prefix tiers and dunk modes: PASS');

// Independent exhaustive enumeration of small problems verifies the optimal objective.
let seed=42;
const rand=n=>{seed=(seed*1664525+1013904223)>>>0;return seed%n};
for(let test=0;test<80;test++){
  const attrs=['A','B','C'],caps=Object.fromEntries(attrs.map(k=>[k,30]));
  const badges=Array.from({length:3},(_,i)=>badge('Badge '+i,[[...Array.from({length:1+rand(2)},()=>Array.from({length:1+rand(2)},()=>[attrs[rand(3)],26+rand(5)]))]]));
  const targets=Object.fromEntries(badges.map(b=>[b.name,1]));
  const result=solve({attrs,caps,badges,targets});
  let best=Infinity;
  for(let A=25;A<=30;A++)for(let B=25;B<=30;B++)for(let C=25;C<=30;C++){
    const v={A,B,C};
    if(badges.every(b=>b.tiers[0].some(rule=>rule.every(([k,n])=>v[k]>=n))))best=Math.min(best,A+B+C-75);
  }
  assert.equal(result.ratingIncreases,best,'Exhaustive comparison '+test);
}
console.log('80 independent exhaustive comparisons: PASS');

assert.equal(knownCost({A:89}),0);
assert.equal(knownCost({A:90}),3);
assert.equal(knownCost({A:91}),6);
assert.equal(knownCost({A:97}),24);
assert.equal(knownCost({A:99,B:90}),33);
const expensiveAttrs=['A','B','C','D'];
const expensiveBadges=expensiveAttrs.map(k=>badge(k,[90,93,96,99].map(n=>[[[k,n]]])));
const costInput={attrs:expensiveAttrs,caps:{A:99,B:99,C:99,D:99},badges:expensiveBadges,targets:{A:4}};
const improved=maximize(costInput);
assert.equal(improved.ok,true);assert.equal(improved.ratings.A,99);assert.ok(improved.knownCost<=99);
const scoreHigh=v=>expensiveAttrs.reduce((sum,k)=>sum+[90,93,96,99].filter(n=>v[k]>=n).length,0);
let bestScore=0;
for(const A of [99])for(const B of [89,90,93,96,99])for(const C of [89,90,93,96,99])for(const D of [89,90,93,96,99]){
  const v={A,B,C,D};if(knownCost(v)<=99)bestScore=Math.max(bestScore,scoreHigh(v));
}
assert.equal(scoreHigh(improved.ratings),bestScore);
assert.equal(maximize({...costInput,targets:{A:4,B:4,C:4,D:4}}).errors[0].type,'budget');
const limited=maximize({...costInput,ceilings:{B:89,C:93,D:25}});
assert.equal(limited.ok,true);assert.equal(limited.ratings.A,99);
assert.ok(limited.ratings.B<=89);assert.ok(limited.ratings.C<=93);assert.equal(limited.ratings.D,25);
const maximumOnly=maximize({...costInput,targets:{},ceilings:{A:25,B:25,C:25,D:25}});
assert.equal(maximumOnly.ok,true);assert.deepEqual(maximumOnly.ratings,{A:25,B:25,C:25,D:25});
console.log('Maximums, fixed ratings, invalid bounds, alternate badge routes and improvement limits: PASS');
const routes=badge('Routes',[[[['A',90]],[['B',80],['C',80]]]]);
const lowCost=solve({attrs:['A','B','C'],caps:{A:99,B:99,C:99},badges:[routes],targets:{Routes:1},knownBudget:99});
assert.equal(lowCost.knownCost,0);assert.equal(lowCost.ratings.B,80);assert.equal(lowCost.ratings.C,80);
console.log('Inclusive 90 boundary, locked minimums, known-cost ceiling, alternative routes and improvement score: PASS');

const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(source);
const ctx=vm.createContext({});
vm.runInContext(source.slice(0,source.indexOf('// ---- state ----'))+';globalThis.fixture={MODEL,BADGES,compute,tierOf};',ctx);
const {MODEL,BADGES,compute,tierOf}=ctx.fixture;
const profiles=Object.keys(MODEL.positions).map(pos=>{const p=MODEL.positions[pos];return {pos,H:p.href,WS:p.href+2,W:p.wref,A:'None',B:'Normal'}});
profiles.push({pos:'SF',H:82,WS:87,W:205,A:'Shoot',B:'Narrow'});
for(const profile of profiles){
  const {v:caps}=compute(profile),targets=Object.fromEntries(BADGES.map(b=>[b.name,tierOf(caps,b)]).filter(([,t])=>t));
  const start=performance.now();
  const result=solve({attrs:Array.from(MODEL.attrs),caps,badges:BADGES,targets});
  assert.equal(result.ok,true);
  for(const [name,t] of Object.entries(targets))assert.ok(tierOf(result.ratings,BADGES.find(b=>b.name===name))>=t);
  for(const k of MODEL.attrs)assert.ok(result.ratings[k]>=25&&result.ratings[k]<=caps[k]);
  console.log(`${profile.pos} ${profile.H}: all available targets jointly met within caps (${Math.round(performance.now()-start)} ms)`);
}
const screenshotProfile=profiles[profiles.length-1];
const screenshotTargets={'Perfect Lays':3,'Relentless Finisher':2,'Traffic Finisher':2,'Limitless Shooter':2,'Relentless Shooter':3,'Tunnel Vision':3,'Quick Draw':3,'Dimer':2,'Glove':1,'Quick Pass':2,'Intimidator':5,'Locks':5,'Thief':2,'Hustler':4};
const beforeMax=performance.now();
const fullPlan=maximize({attrs:Array.from(MODEL.attrs),caps:compute(screenshotProfile).v,badges:BADGES,targets:screenshotTargets,floors:{FT:70}});
assert.equal(fullPlan.ok,true);assert.ok(fullPlan.knownCost<=99);assert.ok(fullPlan.addedTiers>0);assert.ok(fullPlan.ratings.FT>=70);
for(const [name,t] of Object.entries(screenshotTargets))assert.ok(tierOf(fullPlan.ratings,BADGES.find(b=>b.name===name))>=t);
console.log(`Screenshot targets: minimum cost ${fullPlan.minimumKnownCost}, final known cost ${fullPlan.knownCost}/99, +${fullPlan.addedTiers} badge tiers (${Math.round(performance.now()-beforeMax)} ms)`);
const freeThrowLimited=maximize({attrs:Array.from(MODEL.attrs),caps:compute(screenshotProfile).v,badges:BADGES,targets:screenshotTargets,floors:{FT:70},ceilings:{FT:70,DD:80}});
assert.equal(freeThrowLimited.ok,true);assert.equal(freeThrowLimited.ratings.FT,70);assert.ok(freeThrowLimited.ratings.DD<=80);
for(const [name,t] of Object.entries(screenshotTargets))assert.ok(tierOf(freeThrowLimited.ratings,BADGES.find(b=>b.name===name))>=t);
const blockedWhistle=solve({attrs:Array.from(MODEL.attrs),caps:compute(screenshotProfile).v,badges:BADGES,targets:{'Whistle Wizard':2},ceilings:{FT:70}});
assert.equal(blockedWhistle.ok,false);assert.equal(blockedWhistle.errors[0].name,'Whistle Wizard');
console.log('Screenshot targets preserved with Free Throw locked at 70 and Driving Dunk capped at 80: PASS');
const template=fs.readFileSync(path.join(root,'src/template.html'),'utf8');
const model=fs.readFileSync(path.join(root,'src/model.json'),'utf8').trim();
const planner=fs.readFileSync(path.join(root,'src/threshold-planner.js'),'utf8');
assert.equal(html,template.replace('/*MODEL*/',model).replace('/*PLANNER*/',planner));
console.log('Real badge dataset, screenshot profile, built-script syntax and generated file parity: PASS');
