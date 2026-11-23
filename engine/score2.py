import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Lead scoring, six layers:
 1 Site weakness (up to 40): broken, missing, insecure, not phone-friendly, dated, and the phone-screenshot verdict.
 2 Brand gap (up to 10): how far the look falls short of what this kind of business's customers expect.
 3 Choke points (up to 15): where customers get stuck or sent elsewhere to book, order or call.
 4 Business fit (up to 20): how much this niche lives on its website, repeat business, ticket size.
 5 Pressure (up to 5): unclaimed Google profile, few reviews, low rating, no photos.
 6 Proximity (up to 10): distance from 84097, State Street bonus."""
import json,math,re,collections,hashlib,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from profiles import P
S=LE_HOME+'/'
L=S+'leads/';SH=S+'mshots/'
U=json.load(open(L+'uniq.json'));A=json.load(open(L+'audit.json'))
PATHS=json.load(open(L+'paths.json')) if os.path.exists(L+'paths.json') else {}
JV=json.load(open(SH+'_judge.json')) if os.path.exists(SH+'_judge.json') else {}
MM=json.load(open(SH+'_metrics.json')) if os.path.exists(SH+'_metrics.json') else {}
exec(open(os.path.join(os.path.dirname(__file__),'score.py')).read().split('names=collections')[0].split('HIGH=')[0])  # miles(), HOME
CHAINS=re.search(r'CHAINS=r"(.*?)"\n',open(os.path.join(os.path.dirname(__file__),'score.py')).read()).group(1)
names=collections.Counter(re.sub(r"[^a-z]","",x.get('title','').lower())[:18] for x in U)
def addinfo(x):
    out=set()
    for grp in (x.get('additionalInfo') or {}).values():
        for d in grp or []:
            for k,v in d.items():
                if v:out.add(k.lower())
    return out
leads=[]
for x in U:
    if x.get('permanentlyClosed') or x.get('temporarilyClosed') or not x.get('location'):continue
    t=x.get('title','');nm=t.lower();niche=x.get('searchString','');prof=P.get(niche,dict(found="Google",repeat="varies",web=6,look=5,appt=0,ticket="med",why=""))
    if re.search(CHAINS,nm) or names[re.sub(r"[^a-z]","",nm)[:18]]>=3:continue
    loc=(x['location']['lat'],x['location']['lng']);d=miles(HOME,loc)
    site=x.get('website') or '';a=A.get(site,{"kind":"none"}) if site else {"kind":"none"};k=a.get('kind','none')
    h=hashlib.md5(x['placeId'].encode()).hexdigest()[:12];v=JV.get(h) or {};m=MM.get(h,{});pth=PATHS.get(site) or {}
    sig=[];need=0;choke=[];chokept=0
    # 1 site weakness (raw 0-60, scaled to 40)
    if k=="none":need+=40;sig.append(("No website on Google","Google lists no website. Search the name once to be sure."))
    elif k=="social":need+=40;sig.append(("Social page only",f"Their 'website' is {a.get('host')}."))
    elif k=="down":
        if a.get('dead'):need+=45;sig.append(("Website broken",f"It doesn't load for visitors ({a.get('err','')})."))
        else:sig.append(("Couldn't check site","It blocks automated checks; open it yourself."))
    else:
        if a.get('parked'):need+=45;sig.append(("Parked or placeholder","The domain shows a parked or coming-soon page."))
        if not a.get('https'):need+=10;sig.append(("Not secure","No HTTPS; phones show 'Not secure'."))
        if not a.get('viewport') or m.get('overflow'):need+=12;sig.append(("Not built for phones","It's a desktop page squeezed onto a phone."))
        y=a.get('year')
        if y and y<=2019:need+=8;sig.append(("Stale",f"Copyright still says {y}."))
        if a.get('old_builder'):need+=6;sig.append(("Old site builder",f"Built on {a['old_builder']}."))
        if a.get('imgs',0)>=4 and a.get('noalt',0)/max(1,a['imgs'])>=.5:need+=4;sig.append(("Accessibility risk",f"{a['noalt']} of {a['imgs']} images lack alt text (ADA exposure)."))
    vd=v.get('verdict')
    if vd=='redesign':
        need+=25+(5 if v.get('dated',0)>=8 else 0);sig.insert(0,('Site disabled' if 'site disabled' in v.get('flags',[]) else 'Looks outdated on phones',v.get('reason','')))
    elif vd=='maybe':need+=5;sig.insert(0,('Looks so-so on phones',v.get('reason','')))
    elif vd=='skip':need=max(0,need-15);sig.append(('Looks modern on phones',v.get('reason','')))
    weak=round(min(60,need)*40/60)
    # 2 brand gap
    brand=v.get('brand');bg=0
    if k in('none','social') or a.get('dead') or a.get('parked'):bg=min(10,round(prof['look']*.9))
    elif brand:bg=min(10,max(0,round((prof['look']-brand)*1.4)))
    if bg>=5:sig.append(("Brand falls short",v.get('brandnote') or f"Customers of a {niche} expect a better-looking presence."))
    # 3 choke points
    bh=pth.get('book_hosts') or [];info=addinfo(x)
    if prof.get('appt'):
        if k in('none','social') or a.get('dead'):chokept+=8;choke.append("No real site to book on; clients have to call or message")
        elif pth and not bh and not pth.get('form') and not a.get('booking') and not a.get('form') and (not vd or 'no clear call or booking' in v.get('flags',[])):chokept+=6;choke.append("No online booking found; looks phone-only" if not pth.get('dm_to_book') else "Booking happens in DMs")
        elif pth.get('book_link') and not pth.get('book_embed'):chokept+=5;choke.append(f"Booking sends clients off-site to {', '.join(pth['book_link'][:2])}")
        if len(bh)>1:chokept+=3;choke.append(f"Clients bounce between {len(bh)} booking tools ({', '.join(bh[:3])})")
        if pth.get('call_to_book'):chokept+=2;choke.append("The site says to call to book")
    if prof.get('order'):
        tp=[o for o in pth.get('order',[]) if o in('DoorDash','Uber Eats','Grubhub')]
        if tp and not [o for o in pth.get('order',[]) if o not in('DoorDash','Uber Eats','Grubhub')]:chokept+=5;choke.append(f"Online orders go through {', '.join(tp)}, which take a cut")
        elif niche in('florist','clothing boutique','jewelry store','bakery') and k=='ok' and not pth.get('shop') and not pth.get('order'):chokept+=4;choke.append("No way to order or buy online")
    if prof.get('urgent') and (k in('none','social') or (k=='ok' and not a.get('tel'))):chokept+=5;choke.append("No tap-to-call for customers searching in a hurry")
    if not prof.get('appt') and k=='ok' and pth and not pth.get('form') and not a.get('form') and not a.get('booking') and not bh and prof['ticket']=='high' and (not vd or 'no clear call or booking' in v.get('flags',[])):chokept+=3;choke.append("No quote or contact form found")
    chokept=min(15,chokept)
    # 4 business fit
    rep={'every':4}
    fit=round(prof['web']*1.2)+ (4 if any(w in prof['repeat'] for w in('week','every','monthly','daily','for years')) else 2) + {'high':4,'med':2,'low':1}[prof['ticket']]
    rc=x.get('reviewsCount') or 0;rt=x.get('totalScore') or 0
    fit+= 2 if rc>=50 else 1 if rc>=15 else 0
    fit=min(20,fit)
    # 5 pressure
    pres=[]
    if x.get('claimThisBusiness'):pres.append("Google profile is unclaimed")
    if rc<10:pres.append(f"Only {rc} Google reviews")
    if rt and rt<4.0 and rc>=10:pres.append(f"{rt}★ rating")
    if (x.get('imagesCount') or 0)<5:pres.append("Almost no photos on Google")
    prs=min(5,len(pres)*2)
    # 6 pride lift: how big and exciting the upgrade will feel to the owner (distance is not scored; 84097 is only the starting point for the route)
    healthy=2 if (rt>=4.5 and rc>=30) else 1 if rt>=4.2 else 0
    if k in('none','social') or a.get('dead') or a.get('parked'):lift=min(10,round(4+prof['look']*.4+healthy))
    elif v.get('dated'):lift=min(10,max(0,round((v['dated']-3)*.8+prof['look']*.3+healthy)))
    else:lift=min(10,round(prof['look']*.3+healthy))
    prox=lift
    score=weak+bg+chokept+fit+prs+lift
    # Tiers are about quality, not quantity:
    # A = proven need (outdated on a phone, no site, social-only, broken, parked or disabled) + a healthy business (10+ reviews, 4.0+ stars) + a niche where the site matters (fit 14+)
    # B = proven need but a weaker business signal, or a so-so site with a big choke point in a healthy, high-fit business
    proven=vd=='redesign' or k in('none','social') or a.get('dead') or a.get('parked') or 'site disabled' in v.get('flags',[])
    healthy_biz=rc>=10 and rt>=4.0
    if proven and healthy_biz and fit>=14 and score>=55:tier='A'
    elif (proven and fit>=14 and rc>=3) or (vd=='maybe' and healthy_biz and chokept>=8 and fit>=14):tier='B'
    else:tier='C'
    top=[s for s in [choke[0] if choke else None]+[s[1] if s[0] in('No website on Google','Social page only','Website broken') else None for s in sig[:2]] if s]
    angle=prof['why']
    leads.append(dict(id=x['placeId'],n=t,niche=niche,addr=(x.get('address') or '').replace(', USA',''),city=x.get('city'),ph=x.get('phone'),web=site or None,gm=x.get('url'),rt=rt,rc=rc,mi=round(d,1),lat=loc[0],lng=loc[1],
        weak=weak,bg=bg,choke=chokept,fit=fit,prs=prs,prox=prox,score=score,tier=tier,sig=sig,chk=choke,pres=pres,kind=k,
        vis={'v':vd,'d':v.get('dated'),'b':brand,'r':v.get('reason'),'bn':v.get('brandnote')} if vd else None,
        prof={'found':prof['found'],'repeat':prof['repeat'],'web':prof['web'],'look':prof['look']},angle=angle,shot=h if os.path.exists(SH+h+'.jpg') and vd in('redesign','maybe','skip') else None))
for l in leads:
    peers=[p for p in leads if p['niche']==l['niche'] and p['id']!=l['id'] and (p['vis'] or {}).get('v')=='skip']
    peers.sort(key=lambda p:miles((l['lat'],l['lng']),(p['lat'],p['lng'])));l['comp']=[p['n'] for p in peers[:3]]
for l in leads:del l['lat'],l['lng']
leads.sort(key=lambda l:-l['score'])
json.dump(leads,open(L+'leads2.json','w'),separators=(',',':'))
c=collections.Counter(l['tier'] for l in leads);print(len(leads),c)
print('choke',collections.Counter(ch.split(' ')[0]+' '+ch.split(' ')[1] for l in leads for ch in l['chk']).most_common(10))
for l in [l for l in leads if l['tier']=='A'][:8]:print(l['score'],l['n'],l['niche'],'|',l['weak'],l['bg'],l['choke'],l['fit'],l['prs'],l['prox'],'|',l['chk'][:2],[s[0] for s in l['sig'][:3]])
