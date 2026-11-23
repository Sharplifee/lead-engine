import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Mobile-first capture: loads each site as an iPhone, photographs the first two screens, and measures how it behaves on a phone."""
import asyncio,json,hashlib,os
from playwright.async_api import async_playwright
S=LE_HOME+'/'
O=S+'mshots/'
leads=json.load(open(S+'leads/leads.json'))
MET=json.load(open(O+'_metrics.json'))
J=json.load(open(O+'_judge.json'))
DONE=set(json.load(open(O+'_reshot.json'))) if os.path.exists(O+'_reshot.json') else set()
todo=[]
for l in leads:
    if l.get('web') and l['kind'] in('ok','down') and not any(s[0]=='Website broken' for s in l['sig']):
        h=hashlib.md5(l['id'].encode()).hexdigest()[:12]
        if (J.get(h,{}).get('verdict')=='unseen' or ('fail' in MET.get(h,{}))) and h not in DONE:todo.append((h,l['web']))
print('todo',len(todo),flush=True)
PROBE='''()=>{const vw=innerWidth,de=document.documentElement;
 const txt=[...document.querySelectorAll('p,li,a,span,td,div')].filter(e=>e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>3)).slice(0,400);
 let small=0;txt.forEach(e=>{if(parseFloat(getComputedStyle(e).fontSize)<12)small++});
 const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.top<window.innerHeight*2};
 const tel=[...document.querySelectorAll('a[href^="tel:"]')].some(vis);
 const cta=[...document.querySelectorAll('a,button')].filter(vis).some(e=>/book|schedule|appointment|call|quote|order|reserve|contact|estimate/i.test(e.textContent));
 const tiny=[...document.querySelectorAll('a,button')].filter(vis).filter(e=>{const r=e.getBoundingClientRect();return r.height<24&&r.width<24}).length;
 const menu=!!document.querySelector('[aria-label*="menu" i],.hamburger,.menu-toggle,.navbar-toggler,[class*="burger" i],button[aria-expanded]');
 return {overflow:de.scrollWidth>vw+8,smallText:txt.length?Math.round(small/txt.length*100):0,tel,cta,tinyTargets:tiny,menu,pageScreens:Math.round(de.scrollHeight/window.innerHeight)}}'''
async def worker(br,dev,q):
    while True:
        try:h,u=q.get_nowait()
        except asyncio.QueueEmpty:return
        ctx=await br.new_context(**dev,ignore_https_errors=True)
        p=await ctx.new_page()
        try:
            await p.goto(u if '://' in u else 'http://'+u,timeout=40000,wait_until='networkidle')
            await p.wait_for_timeout(6000)
            for t in ['Accept','Accept All','I Agree','Got it','OK','Close','I understand']:
                b=p.get_by_role('button',name=t,exact=False)
                if await b.count():
                    try:await b.first.click(timeout=1500)
                    except Exception:pass
                    break
            await p.wait_for_timeout(1500)
            m=await p.evaluate(PROBE)
            await p.screenshot(path=O+h+'.jpg',type='jpeg',quality=60,clip={'x':0,'y':0,'width':390,'height':1688},full_page=True)
            MET[h]=m
        except Exception as e:MET[h]={'fail':str(e)[:80]}
        finally:await ctx.close()
async def main():
    q=asyncio.Queue()
    for t in todo:q.put_nowait(t)
    async with async_playwright() as pw:
        dev=dict(pw.devices['iPhone 13']);dev['device_scale_factor']=1
        br=await pw.chromium.launch(**({'executable_path':_os.environ['LE_CHROME']} if _os.environ.get('LE_CHROME') else {}))
        async def saver():
            while not q.empty():
                await asyncio.sleep(60);json.dump(MET,open(O+'_metrics.json','w'));print('saved',len(MET),flush=True)
        await asyncio.gather(saver(),*[worker(br,dev,q) for _ in range(10)])
        await br.close()
    J2=json.load(open(O+'_judge.json'))
    for h,_ in todo:J2.pop(h,None);DONE.add(h)
    json.dump(J2,open(O+'_judge.json','w'));json.dump(sorted(DONE),open(O+'_reshot.json','w'))
    json.dump(MET,open(O+'_metrics.json','w'));print('done',sum('fail' not in v for v in MET.values()),'of',len(MET),flush=True)
asyncio.run(main())
