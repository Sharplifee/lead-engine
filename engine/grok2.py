import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Wave 2 step 2: score bot-found businesses with the same layers and tiers, then add them to leads3.json."""
import json,re,hashlib,os,datetime as dt,collections,sys,urllib.parse
S=LE_HOME+'/'
sys.path.insert(0,S+'engine');from profiles import P
R=json.load(open(S+'leads/grok_rows.json'));J=json.load(open(S+'mshots/_judge.json'))
today=dt.date(2026,11,23)
MAP=[(r'nail',"nail salon"),(r'lash|brow|esthetic|skin|facial|spa\b|day spa',"med spa"),(r'barber',"barber shop"),(r'hair|salon|stylist',"hair salon"),(r'massage',"massage therapy"),(r'tattoo|piercing',"tattoo shop"),
 (r'groom|pet|dog',"pet grooming"),(r'daycare|preschool',"daycare"),(r'photograph',"photographer"),(r'plumb',"plumber"),(r'electric',"electrician"),(r'hvac|heating|air',"HVAC"),(r'roof',"roofing contractor"),
 (r'landscap|lawn|sprinkler|tree',"landscaping"),(r'clean|window',"cleaning service"),(r'auto body',"auto body shop"),(r'detail',"auto detailing"),(r'auto|mechanic|oil change|towing',"auto repair"),
 (r'bak|cake|cookie|dessert|pastr|candy|chocolate|toffee|caramel|ice cream',"bakery"),(r'florist|flower',"florist"),(r'jewel',"jewelry store"),(r'boutique|clothing|vintage|thrift|bridal|formal|dancewear',"clothing boutique"),
 (r'restaurant|food truck|grocery|market',"restaurant"),(r'coffee',"coffee shop"),(r'gym|fitness|trainer',"gym"),(r'dance',"dance studio"),(r'dentist|dental',"dentist"),(r'chiro',"chiropractor")]
GEN={'shop':dict(found='Google Maps, Instagram, word of mouth',repeat='occasional to monthly',web=7,look=8,why='Shoppers check the shop online before they visit or buy, so the site has to look as good as the store.'),
 'trade':dict(found='Google search, referrals',repeat='as needed',web=8,look=5,why='Homeowners compare a few contractors online and call the one that looks most credible and easiest to reach.')}
TRADE=r'paint|handyman|contractor|remodel|concrete|floor|fenc|garage|cabinet|excavat|appliance|junk|upholster|tailor|taxiderm|dry clean|piano|music|trainer|tutor'
def prof(bt):
    b=bt.lower()
    for rx,k in MAP:
        if re.search(rx,b):return k,P[k]
    return (b,GEN['trade'] if re.search(TRADE,b) else GEN['shop'])
def ago(s):
    try:return (today-dt.date.fromisoformat((s or '')[:10])).days
    except:return None
def num(x):
    try:return float(x)
    except:return 0
def handle(u):return re.sub(r'^https?://(www\.|m\.)?facebook\.com/','',u or '').strip('/')
out=[];c=collections.Counter()
for r in R:
    niche,p=prof(r['business_type']);look=p['look'];web=p['web']
    h=hashlib.md5(r['id'].encode()).hexdigest()[:12];v=J.get(h) if r['kind'] in('site','builder') else None
    vd=(v or {}).get('verdict');rt=num(r.get('rating'));rc=int(num(r.get('reviews')))
    k=r['kind'];note=(r.get('note') or '').split(' | VERIFIER')[0]
    if k=='none':weak,sig=36,[['No website on Google',note]]
    elif k=='social':weak,sig=34,[['Social page only',note]]
    elif k in('dead','parked'):weak,sig=38,[['Website broken' if k=='dead' else 'Parked domain',note]]
    elif k=='builder':weak,sig=30,[['Booking page only',note]]
    else:
        weak={'redesign':34,'maybe':14,'skip':0}.get(vd,20)
        sig=[['Looks outdated on phones' if vd=='redesign' else 'Site needs work',note]] if vd!='skip' else []
    brand=(v or {}).get('brand') or 0
    bg=min(10,look) if k!='site' else max(0,min(10,look-brand)) if brand else 4
    bk=(r.get('booking') or '').lower();chk=[]
    if re.search(r'call|dm|message|text|email',bk):chk.append('Call or DM to book or order')
    if re.search(r'vagaro|glossgenius|square|booksy|fresha|calendly|pawfinity|moego|myonline|jobber',bk):chk.append('Booking app sends customers off-site')
    if 'in store' in bk and look>=7:chk.append('No way to buy online')
    choke=min(15,len(chk)*7)
    fit=min(20,web*2)
    pres=[]
    if rc<10:pres.append(f"Only {rc} Google reviews" if rc else "No Google reviews")
    if not (r.get('hours_listed') or '').strip():pres.append("No hours on Google")
    if rt and rt<4 and rc>=10:pres.append(f"{rt}★ rating")
    prs=min(5,len(pres)*2)
    healthy=2 if (rt>=4.5 and rc>=30) else 1 if rt>=4.2 else 0
    lift=min(10,round(look*.6+healthy+(2 if k!='site' or vd=='redesign' else 0)))
    score=weak+bg+choke+fit+prs+lift
    ds=[x for x in [ago(r.get('newest_review')),ago(r.get('fb_last_post')),ago(r.get('ig_last_post'))] if x is not None]
    if ds and min(ds)<=120:alive='active'
    elif ds and min(ds)<=365:alive='steady'
    elif ds and not (r.get('hours_listed') or '').strip():alive='dormant'
    else:alive='steady'
    proven=k in('none','social','dead','parked','builder') or vd=='redesign'
    healthy_biz=(rc>=10 and rt>=4.0) or alive=='active'
    if proven and healthy_biz and fit>=14 and score>=55 and alive!='dormant':tier='A'
    elif (proven and fit>=12) or (vd=='maybe' and healthy_biz and choke>=7):tier='B'
    else:tier='C'
    fb=handle(r.get('fb_url'));ig=(r.get('ig_handle') or '').lstrip('@')
    soc={}
    if ig:soc['ig']={'h':ig,'f':int(num(r.get('ig_followers'))) or None,'d':ago(r.get('ig_last_post')),'n':None}
    if fb:soc['fb']={'h':fb,'f':int(num(r.get('fb_followers'))) or None,'d':ago(r.get('fb_last_post'))}
    if k in('none','social'):home='Facebook is their website' if fb and not ig else 'Instagram is their website' if ig else 'Facebook is their website' if fb else 'No real home online'
    else:home='Website'
    act=", ".join(x for x in [f"last Google review {ago(r.get('newest_review'))}d ago" if ago(r.get('newest_review')) is not None else '',f"last Facebook post {ago(r.get('fb_last_post'))}d ago" if ago(r.get('fb_last_post')) is not None else '',f"last Instagram post {ago(r.get('ig_last_post'))}d ago" if ago(r.get('ig_last_post')) is not None else '',"verified open by bot sweep"] if x)
    out.append(dict(id=r['id'],n=r['name'].strip(),niche=niche,addr=(r.get('address') or '').replace(', USA',''),city=r.get('city'),ph=r.get('phone') or None,web=(r.get('website') or None),
      gm="https://www.google.com/maps/search/?api=1&query="+urllib.parse.quote(f"{r['name']} {r.get('address') or r.get('city','')}"),rt=rt or None,rc=rc,mi=None,weak=weak,bg=bg,choke=choke,fit=fit,prs=prs,prox=lift,score=score,tier=tier,
      sig=sig,chk=chk,pres=pres,kind={'site':'ok','builder':'social'}.get(k,k if k!='parked' else 'dead'),vis={'v':vd,'d':(v or {}).get('dated'),'b':brand,'r':(v or {}).get('reason'),'bn':(v or {}).get('brandnote')} if vd else None,
      prof={'found':p['found'],'repeat':p['repeat'],'web':web,'look':look},angle=p['why'],shot=h if vd in('redesign','maybe','skip') and os.path.exists(S+'mshots/'+h+'.jpg') else None,
      comp=[],soc=soc,home=home,alive=alive,act=act,src='bots'))
    c[tier]+=1
json.dump(out,open(S+'leads/grok_scored.json','w'))
L=json.load(open(S+'leads/leads3.json'));L=[l for l in L if l.get('src')!='bots']+out
L.sort(key=lambda l:-int(l['score']))
json.dump(L,open(S+'leads/leads3.json','w'),separators=(',',':'))
print(dict(c),collections.Counter(o['home'] for o in out),len(L))
