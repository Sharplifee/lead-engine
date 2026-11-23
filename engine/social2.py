import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Step 2: match Google results to each business's own Instagram/Facebook, then start profile scrapes."""
import json,re,urllib.request,sys
from urllib.parse import urlparse
S=LE_HOME+'/'
T=open(S+'leads/.tok').read().strip()
R=json.load(open(S+'social/runs.json'));Q=json.load(open(S+'social/q2id.json'))
L={l['id']:l for l in json.load(open(S+'leads/leads2.json')) if l['tier'] in('A','B')}
FS=json.load(open(S+'social/from_sites.json'))
def get(url):return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"Authorization":"Bearer "+T}),timeout=120))
items=[]
for ds in [R['search'][1]]+[x[1] for x in R.get('search_more',[])]:items+=get(f"https://api.apify.com/v2/datasets/{ds}/items?clean=true&format=json")
GEN=set("llc inc co the and of salon studio spa shop studios services service utah orem provo lindon pleasant grove american fork lehi springville spanish fork company center centre auto repair dental family hair nail nails barber barbershop beauty boutique bakery cafe coffee restaurant grill law firm group clinic care pet grooming photography photo media design".split())
def toks(s):return [t for t in re.findall(r"[a-z0-9]+",s.lower()) if len(t)>=3 and t not in GEN]
BAD={'p','reel','reels','explore','stories','popular','hashtag','watch','events','groups','posts','photos','videos','public','people','pages','marketplace','login','share'}
def parse(u):
    p=urlparse(u);host=re.sub(r'^(www\.|m\.|[a-z]{2}-[a-z]{2}\.)','',p.netloc.lower());seg=[x for x in p.path.split('/') if x]
    if not seg or seg[0].lower() in BAD:return None
    if host=='instagram.com':return ('ig',seg[0].lower())
    if host=='facebook.com':return ('fb',seg[0])
    return None
found={}
for it in items:
    q=(it.get('searchQuery') or {}).get('term');lid=Q.get(q)
    if not lid:continue
    l=L[lid];nt=toks(l['n']);out={}
    for r in it.get('organicResults',[]):
        h=parse(r.get('url',''))
        if not h or h[0] in out:continue
        hay=(h[1]+' '+(r.get('title') or '')).lower().replace('.','').replace('_','')
        squash=re.sub(r'[^a-z0-9]','',hay)
        if nt and (any(t in hay for t in nt) or re.sub(r'[^a-z0-9]','',''.join(nt))[:10] in squash):out[h[0]]=h[1]
    found[lid]=out
merged={}
for lid in L:
    m=dict(FS.get(lid,{}));
    for k,v in found.get(lid,{}).items():m.setdefault(k,v)
    merged[lid]=m
json.dump(merged,open(S+'social/merged.json','w'))
import os
have=json.load(open(S+'social/ig.json')) if os.path.exists(S+'social/ig.json') else {}
ig=sorted({m['ig'].lower() for m in merged.values() if m.get('ig')}-set(have))
fbneed=[ (lid,m['fb']) for lid,m in merged.items() if m.get('fb') and (L[lid]['kind'] in('none','social','down') or not m.get('ig'))]
print('leads',len(L),'with ig',sum(1 for m in merged.values() if m.get('ig')),'with fb',sum(1 for m in merged.values() if m.get('fb')),'neither',sum(1 for m in merged.values() if not m.get('ig') and not m.get('fb')),'fb to scrape',len(fbneed))
if '--start' in sys.argv:
    def start(actor,inp,cap):
        r=urllib.request.Request(f"https://api.apify.com/v2/acts/{actor}/runs?maxTotalChargeUsd={cap}",data=json.dumps(inp).encode(),headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
        d=json.load(urllib.request.urlopen(r,timeout=60))['data'];return d['id'],d['defaultDatasetId']
    R['ig2']=start("apify~instagram-profile-scraper",{"usernames":ig},2)
    fbu=[('https://www.facebook.com/'+f) for _,f in fbneed][:320]
    R['fb']=start("apify~facebook-pages-scraper",{"startUrls":[{"url":u} for u in fbu]},2.8)
    json.dump(R,open(S+'social/runs.json','w'));print('started',R['ig2'],R['fb'],len(ig),len(fbu))
