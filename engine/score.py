import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Scores each business: Need (how weak its web presence is), Value (how much a site matters in its niche and whether it can pay), Fit (close to 84097, independent)."""
import json,math,re,collections,sys
L=LE_HOME+'/leads/'
U=json.load(open(L+'uniq.json'));A=json.load(open(L+'audit.json'))
HOME=(40.2745,-111.6853)  # State St & 1300 S, Orem 84097
def miles(a,b):
    R=3958.8;p1,p2=math.radians(a[0]),math.radians(b[0]);dp=p2-p1;dl=math.radians(b[1]-a[1])
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2;return 2*R*math.asin(math.sqrt(h))
HIGH={"dentist","chiropractor","physical therapy","med spa","optometrist","law firm","HVAC","plumber","roofing contractor","electrician","auto body shop","auto repair","landscaping","pest control","veterinarian"}
MID={"hair salon","barber shop","nail salon","massage therapy","tattoo shop","photographer","gym","martial arts","dance studio","daycare","cleaning service","auto detailing","tire shop","insurance agency","accountant","pet grooming"}
CHAINS=r"great clips|supercuts|sport clips|fantastic sams|cost cutters|jiffy lube|midas|firestone|big o tires|discount tire|les schwab|goodyear|meineke|valvoline|grease monkey|massage envy|hand & stone|elements massage|orangetheory|planet fitness|anytime fitness|crunch fitness|gold'?s gym|24 hour fitness|ufc gym|vasa|aspen dental|bright now|western dental|mcdonald|wendy|burger king|taco bell|starbucks|dutch bros|swig|sodalicious|crumbl|subway|chick-fil-a|panda express|cafe rio|costa vida|olive garden|applebee|chili's|domino|papa john|pizza hut|little caesars|jersey mike|jimmy john|state farm|allstate|farmers insurance|american family|edward jones|h&r block|jackson hewitt|kumon|merry maids|molly maid|terminix|orkin|aptive|petsmart|petco|banfield|vca |walmart|target|costco|kohl|ross |tj maxx|ulta|sally beauty|european wax|the joint|lenscrafters|america's best|visionworks|pearle|sephora|nike|apple store|verizon|at&t|t-mobile|ups store|fedex|smile brands|kid to kid|deseret industries|wingers|denny|ihop|village inn|maverik|chevron|7-eleven|sinclair|harmons|smith's|sam's club|home depot|lowe's|autozone|o'reilly|napa auto|caliber collision|maaco|carstar|gerber collision|service experts|one hour heating|mr\. rooter|roto-rooter|benjamin franklin|mr\. electric|servpro|chem-dry|stanley steemer|sprouts|eyeglass world|whole foods|trader joe|natural grocers|ace hardware|big 5|dick's sporting|barnes|hobby lobby|michaels|joann|party city|dollar tree|family dollar|walgreens|cvs|rite aid|intermountain|revere health|instacare|nuvo|mountainstar|kneaders|great harvest|einstein|panera|jamba|tropical smoothie|nothing bundt|cinnabon|krispy kreme|dunkin|baskin|cold stone|yogurtland|menchie|wingstop|buffalo wild|red robin|texas roadhouse|outback|cracker barrel|five guys|in-n-out|culver|arctic circle|del taco|jack in the box|carl's jr|sonic|arby|kfc|popeyes|raising cane|zupas|chipotle|qdoba|noodles|cupbop|waffle love|sweet tooth|fiiz|thirst|tiger nails"
names=collections.Counter(re.sub(r"[^a-z]","",x.get('title','').lower())[:18] for x in U)
leads=[]
for x in U:
    if x.get('permanentlyClosed') or x.get('temporarilyClosed') or not x.get('location'):continue
    t=x.get('title','');nm=t.lower();niche=x.get('searchString','')
    loc=(x['location']['lat'],x['location']['lng']);d=miles(HOME,loc)
    chain=bool(re.search(CHAINS,nm)) or names[re.sub(r"[^a-z]","",nm)[:18]]>=3
    a=A.get(x.get('website') or '',{"kind":"none"});k=a.get('kind','none')
    sig=[];need=0
    if k=="none": need+=40;sig.append(("No website on Google","Google lists no website. Quick-check they do not have one elsewhere."))
    elif k=="social": need+=40;sig.append(("Social page only",f"Their 'website' is {a.get('host')}."))
    elif k=="down":
        e=a.get('err','')
        if a.get('dead'):need+=45;sig.append(("Website broken",f"Their site doesn't load for visitors ({e})."))
        else: sig.append(("Couldn't check site","Their site blocks automated checks; look at it yourself."))
    else:
        if a.get('parked'):need+=45;sig.append(("Parked or placeholder","The domain shows a parked or coming-soon page."))
        if not a.get('https'):need+=12;sig.append(("Not secure","No HTTPS; browsers flag it 'Not secure'."))
        if not a.get('viewport'):need+=15;sig.append(("Not mobile-friendly","No mobile layout; it shrinks to desktop size on phones."))
        y=a.get('year')
        if y and y<=2019:need+=10;sig.append(("Stale",f"Copyright still says {y}."))
        elif y and y<=2022:need+=5;sig.append(("Aging",f"Copyright says {y}."))
        if a.get('old_builder'):need+=8;sig.append(("Old site builder",f"Built on {a['old_builder']}."))
        if (a.get('secs') or 0)>5:need+=5;sig.append(("Slow",f"Took {a['secs']}s to load."))
        if a.get('imgs',0)>=4 and a.get('noalt',0)/max(1,a['imgs'])>=.5:need+=5;sig.append(("Accessibility risk",f"{a['noalt']} of {a['imgs']} images have no alt text (ADA exposure)."))
        if not a.get('tel'):need+=3;sig.append(("No tap-to-call","Phone number isn't clickable."))
        if niche in HIGH|MID and not a.get('booking') and not a.get('form'):need+=4;sig.append(("No way to book","No booking link or contact form found."))
        if not a.get('title') or not a.get('h1'):need+=3
    need=min(need,55)
    rc=x.get('reviewsCount') or 0;rt=x.get('totalScore') or 0
    val=15 if niche in HIGH else 11 if niche in MID else 8
    val+=6 if rc>=100 else 4 if rc>=30 else 2 if rc>=10 else 0
    val+=2 if rt>=4.5 else 0;val=min(val,25)
    pres=[]
    if x.get('claimThisBusiness'):pres.append("Google profile is unclaimed")
    if rc<10:pres.append(f"Only {rc} Google reviews (new or invisible)")
    if rt and rt<4.0 and rc>=10:pres.append(f"{rt}★ rating: reputation pressure")
    if (x.get('imagesCount') or 0)<5:pres.append("Almost no photos on Google")
    fit=(12 if d<=2 else 9 if d<=4 else 6 if d<=7 else 3)+(5 if re.search(r"\bstate st",(x.get('address') or '').lower()) else 0)+3
    score=need+val+fit+min(5,len(pres)*2)
    if chain:continue
    leads.append(dict(id=x.get('placeId'),n=t,niche=niche,cat=x.get('categoryName'),addr=(x.get('address') or '').replace(', USA',''),city=x.get('city'),ph=x.get('phone'),web=x.get('website'),gm=x.get('url'),rt=rt,rc=rc,mi=round(d,1),
        lat=round(loc[0],5),lng=round(loc[1],5),need=need,val=val,fit=fit,score=score,sig=sig,pres=pres,kind=k,state=bool(re.search(r"\bstate st",(x.get('address') or '').lower()))))
# visual layer: Claude-style 2-second look at each homepage screenshot
import hashlib,os
SH=LE_HOME+'/mshots/'
MM=json.load(open(SH+'_metrics.json')) if os.path.exists(SH+'_metrics.json') else {}
JV=json.load(open(SH+'_judge.json')) if os.path.exists(SH+'_judge.json') else {}
for l in leads:
    h=hashlib.md5(l['id'].encode()).hexdigest()[:12];v=JV.get(h)
    l['shot']=h if os.path.exists(SH+h+'.jpg') and v and v.get('verdict') in('redesign','maybe','skip') else None
    l['vis']=None
    m=MM.get(h,{})
    if m.get('overflow'):l['need']=min(60,l['need']+10);l['sig'].append(('Scrolls sideways on phones','The page is wider than a phone screen, so it slides left and right.'))
    if not v or 'verdict' not in v:continue
    vd,dt,rs=v['verdict'],v.get('dated',0),v.get('reason','')
    l['vis']={'v':vd,'d':dt,'r':rs}
    if vd=='redesign':
        lab='Site disabled' if 'site disabled' in v.get('flags',[]) else 'Looks outdated on phones'
        l['need']=min(60,l['need']+25+(5 if dt>=8 else 0));l['sig'].insert(0,(lab,rs))
    elif vd=='maybe':l['need']=min(60,l['need']+5);l['sig'].insert(0,('Looks so-so on phones',rs))
    elif vd=='skip':l['need']=max(0,l['need']-15);l['sig'].append(('Looks modern on phones',rs))
    elif vd=='unseen':l['sig'].append(("Couldn't see site","The page didn't show the business's site to our browser; open it yourself."))
    l['score']=l['need']+l['val']+l['fit']+min(5,len(l['pres'])*2)
# competitor pitch: nearest 3 same-niche businesses with a working site
for l in leads:
    peers=[p for p in leads if p['niche']==l['niche'] and p['id']!=l['id'] and p['kind']=='ok' and (p['vis'] or {}).get('v')=='skip']
    peers.sort(key=lambda p:miles((l['lat'],l['lng']),(p['lat'],p['lng'])))
    l['comp']=[p['n'] for p in peers[:3]]
    l['tier']='A' if l['need']>=35 and l['score']>=60 else 'B' if l['need']>=15 and l['score']>=45 else 'C'
leads.sort(key=lambda l:(-l['score']))
json.dump(leads,open(L+'leads.json','w'),separators=(',',':'))
c=collections.Counter(l['tier'] for l in leads);print(len(leads),c)
print(collections.Counter(s[0] for l in leads for s in l['sig']).most_common())
for l in leads[:12]:print(l['tier'],l['score'],l['n'],'|',l['niche'],'|',l['mi'],'mi |',[s[0] for s in l['sig']],l['pres'])
