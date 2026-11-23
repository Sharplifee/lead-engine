import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Alive & consistent check from fresh Google Maps pulls: latest review date, closed flags, hours."""
import json,urllib.request,datetime as dt
S=LE_HOME+'/'
T=open(S+'leads/.tok').read().strip();R=json.load(open(S+'social/runs.json'))
def get(u):return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":"Bearer "+T}),timeout=180))
items=get(f"https://api.apify.com/v2/datasets/{R['reviews'][1]}/items?clean=true&format=json")
today=dt.date(2026,11,22);out={}
for it in items:
    pid=it.get('placeId');
    if not pid:continue
    ds=[]
    for r in it.get('reviews') or []:
        d=r.get('publishedAtDate')
        if d:ds.append(dt.date.fromisoformat(d[:10]))
    last=max(ds) if ds else None
    oh=it.get('openingHours') or []
    out[pid]={'closed':'perm' if it.get('permanentlyClosed') else ('temp' if it.get('temporarilyClosed') else ''),
              'last':last.isoformat() if last else None,'days':(today-last).days if last else None,
              'hours':len(oh)>0,'n3':sum(1 for d in ds if (today-d).days<=90),'rc':it.get('reviewsCount')}
json.dump(out,open(S+'social/activity.json','w'))
from collections import Counter
c=Counter()
for v in out.values():
    c['closed_'+v['closed']]+=bool(v['closed'])
    d=v['days']
    c['rev<=90' if d is not None and d<=90 else ('rev<=365' if d is not None and d<=365 else ('rev>365' if d is not None else 'norev'))]+=1
    c['nohours']+=not v['hours']
print(len(items),'places',dict(c))
