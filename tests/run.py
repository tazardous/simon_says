"""Tests for Simon Says Party Board: card generators (all 3 levels), full games for 1-4 players at every level
(answering right, then a mixed right/wrong game), act-card trick rules, tile spelling, and layout overflow checks."""
import sys, json
from playwright.sync_api import sync_playwright
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
URL='file://'+__file__.rsplit('/tests/',1)[0]+'/index.html'
fails=[]
def chk(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
CARDS="""(()=>{const out={bad:[],n:0,kinds:{}};
 for(let lv=0;lv<3;lv++) for(const t of ['move','spell','math','nature','shape']) for(let i=0;i<300;i++){
  const c=__SS.makeCard(t,lv); out.n++; const k=lv+t+c.kind; out.kinds[k]=(out.kinds[k]||0)+1;
  const err=m=>out.bad.push([lv,t,m,JSON.stringify(c).slice(0,160)]);
  if(!c.prompt||!c.speak||!c.visual) err('missing text');
  if(c.kind==='choice'){ const oks=c.choices.filter(x=>x.ok).length, labs=c.choices.map(x=>x.label); if(oks!==1) err('ok count '+oks); if(new Set(labs).size!==labs.length) err('dup choices '+labs); if(c.choices.length<2) err('few choices'); }
  else if(c.kind==='tiles'){ if(!c.word||c.word.length<3) err('bad word'); }
  else if(c.kind==='act'){ if(typeof c.simon!=='boolean') err('no simon flag'); if(lv===0&&!c.simon) err('level 1 must not trick'); }
  else err('unknown kind '+c.kind);
 } return out;})()"""
RHYME="""(()=>{const bad=[]; let n=0; const same=(a,b)=>__SS.RSETS.some(s=>s.some(x=>x[0]===a)&&s.some(x=>x[0]===b));
 for(let i=0;i<1500;i++){ const c=__SS.makeCard('shape',2); if(!c.rhyme) continue; n++; const [w,ans]=c.rhyme;
  const good=c.choices.filter(x=>x.ok), others=c.choices.filter(x=>!x.ok);
  if(good.length!==1||!same(w,good[0].label)||good[0].label===w) bad.push(['answer',w,good.map(x=>x.label)]);
  for(const o of others) if(same(w,o.label)||o.label===w) bad.push(['distractor rhymes',w,o.label]); }
 return {n,bad}; })()"""
PLAY="""async(mode)=>{ // mode: 'right' always right; 'mixed' ~ half right
  const S=__SS, sleep=ms=>new Promise(r=>setTimeout(r,ms)); let guard=0, turns=0, wrongs=0;
  while(!S.G.over&&guard++<2000){
    if(!document.querySelector('#modal.on')){ document.querySelector('#roll').click(); await sleep(15); continue; }
    const c=S.card, st=S.cardState; if(st.done){ document.querySelector('#next').click(); turns++; await sleep(5); continue; }
    const wantRight=mode==='right'||Math.random()<0.55; if(!wantRight) wrongs++;
    if(c.kind==='choice'){ const bs=[...document.querySelectorAll('#choices button')]; const idx=bs.findIndex(b=>(b.dataset.ok==='1')===wantRight); (bs[idx>=0?idx:0]).click(); }
    else if(c.kind==='act'){ const bs=document.querySelectorAll('#choices button'); const did=wantRight?c.simon:!c.simon; if(did) bs[0].click(); else (bs[1]||bs[0]).click(); }
    else { const w=c.word.split(''); for(let i=0;i<w.length;i++){ const bs=[...document.querySelectorAll('#choices button')].filter(b=>!b.disabled&&b.textContent===w[i]); if(!wantRight&&i===0){ const wr=[...document.querySelectorAll('#choices button')].filter(b=>!b.disabled&&b.textContent!==w[0]); if(wr[0]){ wr[0].click(); wr[0].click(); } const wr2=[...document.querySelectorAll('#choices button')].filter(b=>!b.disabled&&b.textContent!==w[0]); if(wr2[0]) wr2[0].click(); } (document.querySelectorAll('#choices button')&&bs[0]).click(); } }
    await sleep(5);
  }
  const G=S.G; return {over:G.over,scores:G.players.map(p=>p.score),turns,winner:G.players.findIndex(p=>p.score>=S.GOAL),shown:document.querySelector('#win').classList.contains('on'),wrongs};
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':900,'height':640}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'Failed to load' not in m.text else None)
    pg.add_init_script('window.__SSfast=true;'); pg.goto(URL); pg.wait_for_timeout(500)
    r=pg.evaluate(CARDS); chk(not r['bad'],f"{r['n']} generated cards valid {r['bad'][:3]}"); print(' kinds:',json.dumps(r['kinds']))
    r=pg.evaluate(RHYME); chk(r['n']>100 and not r['bad'],f"rhyme cards: {r['n']} checked, answer rhymes and distractors do not {r['bad'][:3]}")
    for lv in range(3):
        for n in (1,2,4):
            pg.evaluate(f'__SS.newGame({{players:{n},level:{lv},avs:[0,1,2,3]}});0')
            r=pg.evaluate(PLAY,'right'); ok=r['over'] and r['shown'] and r['winner']==0 and max(r['scores'])==10
            chk(ok,f'level {lv+1} players {n} all-right game -> {json.dumps(r)}')
            pg.evaluate("document.querySelector('#win').classList.remove('on');0")
        pg.evaluate(f'__SS.newGame({{players:3,level:{lv},avs:[0,1,2,3]}});0')
        r=pg.evaluate(PLAY,'mixed'); chk(r['over'] and r['shown'] and max(r['scores'])==10 and r['wrongs']>0,f'level {lv+1} mixed game -> {json.dumps(r)}')
        pg.evaluate("document.querySelector('#win').classList.remove('on');0")
    # trick rule: no-Simon card, staying still is right
    pg.evaluate('__SS.newGame({players:1,level:2,avs:[0]});0')
    res=pg.evaluate("""(()=>{ const S=__SS; let out=[]; for(const simon of [true,false]){ let c; do{ c=S.makeCard('move',2);}while(c.simon!==simon); out.push([simon,c.banner,c.speak.startsWith('Simon says')]); } return out; })()""")
    chk(res[0][2] and not res[1][2],'speech says "Simon says" only on Simon cards '+json.dumps(res))
    # layout: setup + game at phone portrait, phone landscape, tablet
    for w,h in ((390,780),(844,390),(1024,768)):
        pg.set_viewport_size({'width':w,'height':h}); pg.evaluate("__SS.newGame({players:4,level:1,avs:[0,1,2,3]});0"); pg.wait_for_timeout(100)
        ov=pg.evaluate("(()=>{const b=document.querySelector('#board').getBoundingClientRect(), c=document.querySelector('#center'); return {bw:b.width,bh:b.height,right:b.right,bottom:b.bottom,vw:innerWidth,vh:innerHeight,sw:document.documentElement.scrollWidth,cfit:c.scrollHeight<=c.clientHeight+1}})()")
        chk(ov['right']<=ov['vw']+1 and ov['bottom']<=ov['vh']+1 and ov['sw']<=ov['vw']+1 and ov['cfit'],f'board and centre fit at {w}x{h} {ov}')
    chk(not errs,'no console errors '+str(errs[:3]))
    b.close()
print('FAILS',len(fails)); sys.exit(1 if fails else 0)
