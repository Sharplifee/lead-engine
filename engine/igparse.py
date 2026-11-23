import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import json,urllib.request,sys
T=open('leads/.tok').read().strip();R=json.load(open('social/runs.json'))
out=json.load(open('social/ig.json')) if __import__('os').path.exists('social/ig.json') else {}
for key in sys.argv[1:]:
    ds=R[key][1]
    items=json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.apify.com/v2/datasets/{ds}/items?clean=true&format=json",headers={"Authorization":"Bearer "+T}),timeout=180))
    for it in items:
        u=(it.get('username') or '').lower()
        if not u:continue
        if it.get('error'):out[u]={'missing':True};continue
        ts=[p.get('timestamp') for p in it.get('latestPosts') or [] if p.get('timestamp')]
        out[u]={'f':it.get('followersCount'),'n':it.get('postsCount'),'last':max(ts) if ts else None,'bio':(it.get('externalUrl') or None),'biz':it.get('isBusinessAccount'),'priv':it.get('private')}
json.dump(out,open('social/ig.json','w'))
v=[x for x in out.values() if not x.get('missing')]
print(len(out),'profiles',len(v),'found',sum(1 for x in v if x.get('last')),'with post dates')
