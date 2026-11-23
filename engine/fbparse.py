import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import json,urllib.request,re
T=open('leads/.tok').read().strip();R=json.load(open('social/runs.json'))
items=json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.apify.com/v2/datasets/{R['fb'][1]}/items?clean=true&format=json",headers={"Authorization":"Bearer "+T}),timeout=180))
out={}
for it in items:
    u=it.get('facebookUrl') or it.get('url') or it.get('pageUrl') or ''
    h=re.sub(r'^https?://(www\.|m\.)?facebook\.com/','',u).strip('/')
    if not h:continue
    out[h]={'f':it.get('followers') or it.get('likes'),'last':None,'title':it.get('title'),'personal':bool(it.get('personalProfile'))}
    out[h.lower()]=out[h]
json.dump(out,open('social/fb.json','w'));print(len(items),'fb pages',list(items[0].keys())[:40] if items else '')
