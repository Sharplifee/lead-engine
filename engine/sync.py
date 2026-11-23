"""Sync the engine's data with Supabase (Corpus HQ lbvaosyfikkpvcwksiph).
  python3 engine/sync.py push   -> upsert leads/leads3.json into table lead_engine_leads,
                                   upload screenshots to Storage lead-engine/shots/, working data to lead-engine/data/
  python3 engine/sync.py pull   -> download working data + screenshots so any machine can rebuild
"""
import os,sys,json,glob,urllib.request,urllib.parse,concurrent.futures as cf
LE_HOME=os.environ.get('LE_HOME',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,LE_HOME+'/engine');from keys import secret,SB
K=secret();H={'apikey':K,'Authorization':'Bearer '+K}
BUCKET='lead-engine'
DATA=['leads/*.json','social/*.json','mshots/_*.json','grok_in/*.csv','grok_in_bot*.csv']
def req(url,data=None,method='GET',headers=None,timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url,data=data,method=method,headers={**H,**(headers or {})}),timeout=timeout)
def up(rel,ctype):
    with open(LE_HOME+'/'+rel,'rb') as f:b=f.read()
    req(f"{SB}/storage/v1/object/{BUCKET}/{urllib.parse.quote(rel)}",b,'POST',{'Content-Type':ctype,'x-upsert':'true'}).read();return rel
def row(l):
    return dict(id=l['id'],name=l['n'],niche=l.get('niche'),city=l.get('city'),address=l.get('addr'),phone=l.get('ph'),website=l.get('web'),maps_url=l.get('gm'),
      rating=float(l['rt']) if l.get('rt') not in(None,'') else None,reviews=int(float(l['rc'])) if l.get('rc') not in(None,'') else None,tier=l.get('tier'),score=int(float(l.get('score') or 0)),
      layers={k:l.get(k) for k in('weak','bg','choke','fit','prs','prox')},site_kind=l.get('kind'),presence=l.get('home'),alive=l.get('alive'),activity=l.get('act'),
      signals=l.get('sig'),choke_points=l.get('chk'),pressure=l.get('pres'),vision=l.get('vis'),social=l.get('soc'),profile=l.get('prof'),angle=l.get('angle'),
      nearby_competitors=l.get('comp'),source=l.get('src') or 'maps',screenshot_path=f"mshots/{l['shot']}.jpg" if l.get('shot') else None)
def push():
    L=json.load(open(LE_HOME+'/leads/leads3.json'));rows=[row(l) for l in L]
    for i in range(0,len(rows),500):
        req(SB+'/rest/v1/lead_engine_leads?on_conflict=id',json.dumps(rows[i:i+500]).encode(),'POST',{'Content-Type':'application/json','Prefer':'resolution=merge-duplicates,return=minimal'}).read()
    print('leads upserted',len(rows))
    files=[(os.path.relpath(p,LE_HOME),'application/json' if p.endswith('.json') else 'text/csv') for pat in DATA for p in glob.glob(LE_HOME+'/'+pat)]
    shots=[(os.path.relpath(p,LE_HOME),'image/jpeg') for p in glob.glob(LE_HOME+'/mshots/*.jpg')]
    done=set(open(LE_HOME+'/.pushed').read().split()) if os.path.exists(LE_HOME+'/.pushed') else set()
    shots=[s for s in shots if s[0] not in done]
    with cf.ThreadPoolExecutor(8) as ex:
        n=0
        for r in ex.map(lambda a:up(*a),files+shots):
            n+=1
            if r.startswith('mshots/') and not r.split('/')[-1].startswith('_'):done.add(r)
    open(LE_HOME+'/.pushed','w').write('\n'.join(sorted(done)))
    print('uploaded',len(files),'data files and',len(shots),'new screenshots')
def listing(prefix):
    out=[];off=0
    while True:
        r=json.load(req(f"{SB}/storage/v1/object/list/{BUCKET}",json.dumps({'prefix':prefix,'limit':1000,'offset':off}).encode(),'POST',{'Content-Type':'application/json'}))
        out+=[prefix+'/'+o['name'] for o in r if o.get('id')]
        dirs=[prefix+'/'+o['name'] for o in r if not o.get('id')]
        for d in dirs:out+=listing(d)
        if len(r)<1000:return out
        off+=1000
def down(rel):
    p=LE_HOME+'/'+rel;os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,'wb').write(req(f"{SB}/storage/v1/object/{BUCKET}/{urllib.parse.quote(rel)}").read());return rel
def pull():
    names=[n for pre in('leads','social','mshots','grok_in') for n in listing(pre)]
    try:names+=[n for n in listing('') if n.startswith('/grok_in_bot')]
    except Exception:pass
    names=[n.lstrip('/') for n in names]
    with cf.ThreadPoolExecutor(8) as ex:print('downloaded',sum(1 for _ in ex.map(down,names)))
if __name__=='__main__':{'push':push,'pull':pull}[sys.argv[1] if len(sys.argv)>1 else 'push']()
