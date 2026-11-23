import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Wave 2 step 1: apply verifier fixes, drop chains/closed, dedupe vs existing 3,002 and across bots, classify presence."""
import csv,glob,json,re,hashlib,collections
S=LE_HOME+'/'
digits=lambda p:re.sub(r'\D','',p or '')[-10:]
norm=lambda n:re.sub(r'[^a-z0-9]','',(n or '').lower().split('|')[0])
V={}
for r in csv.DictReader(open(S+'grok_in_bot9.csv',encoding='utf-8')):V[(r['source_bot'],norm(r['name']))]=r
old=json.load(open(S+'leads/uniq.json'))
seenP={digits(x.get('phone')) for x in old if digits(x.get('phone'))}
seenN={norm(x.get('title')) for x in old}
BOOK=r'glossgenius|square\.site|squareup\.com|vagaro|booksy|fresha|calendly|myonlineappointment|mysalononline|pawfinity|linktr\.ee|tr\.ee/|hotplate|etsy\.com|jobbersites|canva\.site|sites\.google\.com|godaddysites|wixsite|business\.site|company\.site|myshopify|kit\.com|vercel\.app'
out={};c=collections.Counter()
for fn in sorted(glob.glob(S+'grok_in/bot*.csv')):
    bot=fn.rsplit('/',1)[1][:-4]
    for r in csv.DictReader(open(fn,encoding='utf-8',errors='replace')):
        if not (r.get('name') or '').strip():continue
        v=V.get((bot,norm(r['name'])))
        if v:
            if v['verdict'] in('chain-franchise','closed'):c['dropped '+v['verdict']]+=1;continue
            if v['verdict']=='wrong match' and v['corrected_field']:
                fs=[f.strip() for f in v['corrected_field'].split(';')];vs=[x.strip() for x in v['corrected_value'].split(';')]
                for f,x in zip(fs,vs):
                    if f in r:r[f]=x
                c['fixed']+=1
        p=digits(r.get('phone'));k=norm(r['name'])
        if (p and p in seenP) or k in seenN:c['already had']+=1;continue
        key=p or k
        if key in out:
            o=out[key]
            for f,x in r.items():
                if x and not o.get(f):o[f]=x
            c['dup across bots']+=1;continue
        r['bot']=bot;out[key]=r
rows=list(out.values())
for r in rows:
    w=(r.get('website') or '').strip();st=(r.get('site_status') or '').lower()
    if not w or st=='none':r['kind']='none'
    elif re.search(r'facebook\.com|instagram\.com',w) or 'social' in st:r['kind']='social'
    elif st in('dead','parked'):r['kind']=st
    elif re.search(BOOK,w,re.I):r['kind']='builder'
    else:r['kind']='site'
    r['id']='g_'+hashlib.md5(((digits(r.get('phone')) or '')+norm(r['name'])).encode()).hexdigest()[:16]
json.dump(rows,open(S+'leads/grok_rows.json','w'))
print(len(rows),'new businesses',dict(c));print(collections.Counter(r['kind'] for r in rows));print(collections.Counter(r['bot'] for r in rows))
