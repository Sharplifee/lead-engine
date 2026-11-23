import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Fold bot details for businesses already in the engine into their existing lead cards (social pages, recency, presence)."""
import json,csv,glob,re,datetime as dt,collections
S=LE_HOME+'/'
digits=lambda p:re.sub(r'\D','',p or '')[-10:]
norm=lambda n:re.sub(r'[^a-z0-9]','',(n or '').lower())
today=dt.date(2026,11,23)
def ago(s):
    try:return (today-dt.date.fromisoformat((s or '')[:10])).days
    except:return None
L=json.load(open(S+'leads/leads3.json'))
byP={};byN={}
for l in L:
    if l.get('src')=='bots':continue
    if digits(l.get('ph')):byP.setdefault(digits(l['ph']),l)
    byN.setdefault(norm(l['n']),l)
bad={(r['source_bot'],norm(r['name'])) for r in csv.DictReader(open(S+'grok_in_bot9.csv',encoding='utf-8')) if r['verdict'] in('wrong match','chain-franchise','closed')}
c=collections.Counter();touched=set()
for fn in sorted(glob.glob(S+'grok_in/bot*.csv')):
    bot=fn.rsplit('/',1)[1][:-4]
    for r in csv.DictReader(open(fn,encoding='utf-8',errors='replace')):
        if not (r.get('name') or '').strip() or (bot,norm(r['name'])) in bad:continue
        l=byP.get(digits(r.get('phone'))) or byN.get(norm(r['name']))
        if not l:continue
        c['matched']+=1;touched.add(l['id'])
        soc=l.setdefault('soc',{}) if l.get('soc') is not None else l.setdefault('soc',{})
        if l.get('soc') is None:l['soc']={};soc=l['soc']
        fb=re.sub(r'^https?://(www\.|m\.)?facebook\.com/','',r.get('fb_url') or '').strip('/');ig=(r.get('ig_handle') or '').lstrip('@').strip()
        if fb and 'fb' not in soc:soc['fb']={'h':fb,'f':int(float(r['fb_followers'])) if (r.get('fb_followers') or '').replace('.','',1).isdigit() else None,'d':ago(r.get('fb_last_post'))};c['added facebook']+=1
        elif fb and soc['fb'].get('d') is None and ago(r.get('fb_last_post')) is not None:soc['fb']['d']=ago(r.get('fb_last_post'));soc['fb']['f']=soc['fb'].get('f') or (int(float(r['fb_followers'])) if (r.get('fb_followers') or '').replace('.','',1).isdigit() else None);c['filled facebook dates']+=1
        if ig and 'ig' not in soc:soc['ig']={'h':ig,'f':None,'d':ago(r.get('ig_last_post')),'n':None};c['added instagram']+=1
        if l.get('kind') in('none','social') and l.get('home') in(None,'No real home online','Website'):
            nh='Facebook is their website' if soc.get('fb') and not soc.get('ig') else 'Instagram is their website' if soc.get('ig') else l.get('home')
            if nh!=l.get('home'):l['home']=nh;c['presence updated']+=1
        ds=[x for x in [ago(r.get('newest_review')),(soc.get('fb') or {}).get('d'),(soc.get('ig') or {}).get('d')] if x is not None]
        if ds and min(ds)<=120 and l.get('alive') in('dormant','steady','unchecked'):
            old=l['alive'];l['alive']='active';c['now active']+=1
            if old=='dormant' and l['tier']=='B':l['tier']='A';c['re-promoted']+=1
        note=' Bot sweep confirmed still open.'
        if 'Bot sweep' not in (l.get('act') or ''):l['act']=((l.get('act') or '')+('; ' if l.get('act') else '')+'confirmed open by bot sweep')
json.dump(L,open(S+'leads/leads3.json','w'),separators=(',',':'))
print(len(touched),'existing leads updated',dict(c))
