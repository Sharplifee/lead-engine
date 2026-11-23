import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Step 1 (free): pull Instagram/Facebook/TikTok links straight off each A/B lead's website."""
import json,re,urllib.request,concurrent.futures as cf
from urllib.parse import urlparse
S=LE_HOME+'/'
L=[l for l in json.load(open(S+'leads/leads2.json')) if l['tier'] in('A','B')]
A=json.load(open(S+'leads/audit.json'))
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
BAD={'sharer','share','intent','plugins','dialog','tr','p','reel','reels','explore','stories','hashtag','watch','events','groups','photo','photos','video','videos','posts','permalink.php','login','privacy','policies','help','ads','business','profile.php'}
def handle(u):
    p=urlparse(u);host=re.sub(r'^(www\.|m\.)','',p.netloc.lower())
    seg=[x for x in p.path.split('/') if x]
    if not seg:return None
    if 'instagram.com' in host and seg[0].lower() not in BAD:return ('ig',seg[0].lower())
    if ('facebook.com' in host or host=='fb.com') and seg[0].lower() not in BAD:return ('fb',seg[0])
    if 'facebook.com' in host and seg[0]=='profile.php' and 'id=' in p.query:return ('fb','profile.php?'+p.query.split('&')[0])
    if 'tiktok.com' in host and seg[0].startswith('@'):return ('tt',seg[0])
    return None
def run(l):
    site=l['web'];out={}
    if not site:return l['id'],out
    if l['kind']=='social':
        h=handle(site if '://' in site else 'https://'+site)
        if h:out[h[0]]=h[1]
        return l['id'],out
    if l['kind']!='ok':return l['id'],out
    try:
        u=A.get(site,{}).get('final') or (site if '://' in site else 'http://'+site)
        html=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=15).read(800000).decode('utf-8','ignore')
    except Exception:return l['id'],out
    for h in re.findall(r'href=["\']([^"\']+)',html,re.I):
        r=handle(h)
        if r and r[0] not in out:out[r[0]]=r[1]
    return l['id'],out
res={}
with cf.ThreadPoolExecutor(14) as ex:
    for i,o in ex.map(run,L):res[i]=o
json.dump(res,open(S+'social/from_sites.json','w'))
print(len(L),'ig',sum('ig' in v for v in res.values()),'fb',sum('fb' in v for v in res.values()),'tt',sum('tt' in v for v in res.values()))
