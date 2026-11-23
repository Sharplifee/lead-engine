import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Vision judge (Gemini; never OpenAI, never key 445): looks at each homepage screenshot the way a person would in 2-3 seconds."""
import json,base64,io,os,sys,concurrent.futures as cf,urllib.request,time
from PIL import Image
S=LE_HOME+'/'
OUT=S+'mshots/_judge.json'
MET=json.load(open(S+'mshots/_metrics.json'))
import hashlib
NICHE={hashlib.md5(l['id'].encode()).hexdigest()[:12]:(l['niche'],l['n']) for l in json.load(open(S+'leads/leads.json'))}
NICHE.update({hashlib.md5(l['id'].encode()).hexdigest()[:12]:(l['business_type'],l['name']) for l in json.load(open(S+'leads/grok_rows.json'))})
J=json.load(open(OUT)) if os.path.exists(OUT) else {}
DONE={k for k,v in J.items() if 'verdict' in v and str(v.get('by','')).startswith('gemini')}
PROMPT="""You are screening local small-business websites for a web designer who rebuilds outdated sites. Most customers will see these sites on a phone, so judge the MOBILE experience first.
This is NAME, a BUSINESS. The image is the top two screens of its homepage on an iPhone. Judge it the way an experienced designer would in 2-3 seconds, weighing: overall design and how current it looks; UI (readability, spacing, hierarchy, tap-friendly buttons, a clear mobile menu); features (an obvious way to call, book, order or get a quote near the top); and function (does it fit the phone, or is it a shrunk desktop page, cut off, overlapping or broken).
Automated hints (can be wrong; trust what you see in the image): MEASURED
Also judge brand fit: how well the look matches what customers of a BUSINESS expect. Beauty, lash, nail, hair, barber, tattoo, boutique, cafe, bakery and similar image-driven businesses should look beautiful, current and share-worthy, because clients pick them by looks and send the link to friends; trades and professional services should look trustworthy, credible and established.
Reply with JSON only: {"verdict":"redesign"|"maybe"|"skip"|"unseen","dated":1-10,"brand":1-10,"reason":"under 16 words, plain English, specific to what you see on the phone","brandnote":"under 12 words on brand fit for this kind of business","flags":[...]}
dated: 1 = modern and polished on mobile, 10 = clearly 2000s-2010s era or unusable on a phone.
verdict, from a typical customer's point of view:
"redesign" = it looks old, cheap, amateur or broken on a phone: early-2010s styling, a shrunk desktop page, cramped tiny text, clashing colors, clip-art or low-res images, cut-off or overlapping layout, or a disabled, parked or under-construction page.
"maybe" = it works and isn't embarrassing, but it's plain, generic or noticeably behind its competitors.
"skip" = a professionally built, current-looking site (most sites built in the last 5 years on modern platforms belong here), even if the call or booking button is further down the page. Chat bubbles and cookie notices are normal and not a reason to mark it down.
Rate "dated" honestly across the full range: a clean modern site is 1-3, plain but fine is 4-6, clearly old or broken is 7-10.
Use "unseen" (dated 0) only when you cannot see the business's own site: a blank or single-color screen, a network or proxy error, a bot or security check, or a cookie or popup wall covering nearly everything.
flags: any of ["not built for phones","dated design","cluttered","hard to read","tiny buttons","no clear call or booking","broken layout","generic template","site disabled","low-quality images","modern"]"""
GKEYS=[open(S+'leads/.gem1').read().strip(),open(S+'leads/.gem2').read().strip()]
GURL="https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
import threading,re as _re
# Free tier allows about 15 requests a minute per model per project, so pace each (model, key) lane at 14/min.
# gemini-flash-lite-latest lanes are always tried first; gemini-flash-latest is the fallback.
LANES=[{'m':m,'k':k,'next':0.0} for m in ("gemini-flash-lite-latest","gemini-flash-latest") for k in GKEYS]
LOCK=threading.Lock();GAP=60/14
def lane():
    while True:
        with LOCK:
            now=time.time()
            if all(L['next']==float('inf') for L in LANES):return None
            for L in LANES:
                if L['next']<=now:L['next']=now+GAP;return L
            wait=min(L['next'] for L in LANES)-now
        time.sleep(max(0.2,wait))
def judge(h):
    m=MET.get(h,{})
    meas=f"sideways scrolling: {'yes' if m.get('overflow') else 'no'}; tap-to-call link near top: {'yes' if m.get('tel') else 'not found'}"
    nn=NICHE.get(h,('local business','This business'))
    prompt=PROMPT.replace('MEASURED',meas).replace('BUSINESS',nn[0]).replace('NAME',nn[1])
    img=Image.open(S+'mshots/'+h+'.jpg').convert('RGB');img.thumbnail((390,1688))
    b=io.BytesIO();img.save(b,'JPEG',quality=70)
    body=json.dumps({"contents":[{"parts":[{"inline_data":{"mime_type":"image/jpeg","data":base64.b64encode(b.getvalue()).decode()}},{"text":prompt}]}],"generationConfig":{"temperature":0,"responseMimeType":"application/json"}}).encode()
    for att in range(12):
        L=lane()
        if L is None:return h,{"error":"daily quota used up"}
        try:
            r=urllib.request.urlopen(urllib.request.Request(GURL.format(m=L['m']),data=body,headers={"x-goog-api-key":L['k'],"Content-Type":"application/json"}),timeout=90)
            t=json.load(r)['candidates'][0]['content']['parts'][0]['text']
            t=t[t.index('{'):t.rindex('}')+1];v=json.loads(t);v['by']=L['m'];return h,v
        except urllib.error.HTTPError as e:
            if e.code in(429,503):
                txt=e.read().decode('utf-8','replace');d=_re.search(r'"retryDelay": "(\d+)s"',txt)
                # A per-day quota hit retires that lane until tomorrow; per-minute hits wait the suggested delay.
                with LOCK:L['next']=float('inf') if 'PerDay' in txt else time.time()+max(10,int(d.group(1)) if d else 10)
                continue
            time.sleep(2)
        except Exception:time.sleep(2)
    return h,{"error":"failed"}
st=json.load(open(S+'shots/_status.json')) if os.path.exists(S+'shots/_status.json') else {}
MET=json.load(open(S+'mshots/_metrics.json'))
import hashlib
NICHE={hashlib.md5(l['id'].encode()).hexdigest()[:12]:(l['niche'],l['n']) for l in json.load(open(S+'leads/leads.json'))}
NICHE.update({hashlib.md5(l['id'].encode()).hexdigest()[:12]:(l['business_type'],l['name']) for l in json.load(open(S+'leads/grok_rows.json'))})
todo=[f[:-4] for f in os.listdir(S+'mshots') if f.endswith('.jpg') and f[:-4] not in DONE and f[:-4] in MET and 'fail' not in MET[f[:-4]]]
print('judging',len(todo),flush=True)
n=0
with cf.ThreadPoolExecutor(int(os.environ.get('CONC','8'))) as ex:
    for h,r in ex.map(judge,todo):
        if r.get('error'):continue
        J[h]=r;n+=1
        if n%50==0:json.dump(J,open(OUT,'w'));print(n,flush=True)
json.dump(J,open(OUT,'w'))
import collections;print(collections.Counter(v.get('verdict',v.get('error')) for v in J.values()))
