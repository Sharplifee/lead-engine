import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Fold Bot 8 enrichment (business pages, recency, hours) into the existing tier A/B lead cards by lead_id."""
import csv,json,re,datetime as dt,collections
S=LE_HOME+'/'
today=dt.date(2026,11,23)
def ago(s):
    try:return (today-dt.date.fromisoformat((s or '')[:10])).days
    except:return None
def n(x):
    try:return int(float(str(x).replace(',','')))
    except:return None
L=json.load(open(S+'leads/leads3.json'));by={l['id']:l for l in L};c=collections.Counter()
for r in csv.DictReader(open(S+'grok_in_bot8.csv',encoding='utf-8',errors='replace')):
    l=by.get(r['lead_id'])
    if not l:c['no match']+=1;continue
    c['matched']+=1;soc=l.get('soc') or {};l['soc']=soc
    fb=re.sub(r'^https?://(www\.|m\.)?facebook\.com/','',r.get('fb_url') or '').strip('/');ig=(r.get('ig_handle') or '').lstrip('@').strip()
    if fb:
        if 'fb' not in soc:soc['fb']={'h':fb,'f':None,'d':None};c['added facebook']+=1
        if n(r.get('fb_followers')) and not soc['fb'].get('f'):soc['fb']['f']=n(r['fb_followers'])
        if ago(r.get('fb_last_post')) is not None and soc['fb'].get('d') is None:soc['fb']['d']=ago(r['fb_last_post'])
    if ig:
        if 'ig' not in soc:soc['ig']={'h':ig,'f':None,'d':None,'n':None};c['added instagram']+=1
        if n(r.get('ig_followers')) and not soc['ig'].get('f'):soc['ig']['f']=n(r['ig_followers'])
        if ago(r.get('ig_last_post')) is not None and soc['ig'].get('d') is None:soc['ig']['d']=ago(r['ig_last_post'])
    if l.get('kind') in('none','social') and l.get('home')=='No real home online' and (soc.get('fb') or soc.get('ig')):
        l['home']='Facebook is their website' if soc.get('fb') and not soc.get('ig') else 'Instagram is their website';c['presence updated']+=1
    ds=[x for x in [ago(r.get('newest_review')),(soc.get('fb') or {}).get('d'),(soc.get('ig') or {}).get('d')] if x is not None]
    if ds and min(ds)<=120 and l.get('alive')!='active':
        if l.get('alive')=='dormant' and l['tier']=='B':l['tier']='A';c['re-promoted']+=1
        l['alive']='active';c['now active']+=1
    if re.search(r'permanently closed|out of business|no longer operat',r.get('note') or '',re.I):l['alive']='closed';l['tier']='C';c['closed']+=1
    if 'Bot 8' not in (l.get('act') or ''):l['act']=(l.get('act') or '')+('; ' if l.get('act') else '')+'pages checked by Bot 8'
json.dump(L,open(S+'leads/leads3.json','w'),separators=(',',':'))
print(dict(c))
