import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Website auditor: fetches each lead's homepage and records plain signals."""
import json,re,sys,time,concurrent.futures as cf,urllib.request,ssl,socket
from urllib.parse import urlparse
SOCIAL=("facebook.com","instagram.com","linktr.ee","yelp.com","business.site","g.page","tiktok.com","x.com","twitter.com","linkedin.com","nextdoor.com","square.site","booksy.com","vagaro.com","schedulicity.com","styleseat.com","genbook.com","mindbodyonline.com")
OLDB={"godaddy builder":r"img1\.wsimg\.com|godaddy\.com/websites|Starfield Technologies","weebly":r"weebly\.com|editmysite","homestead":r"homestead\.com","webs.com":r"webs\.com|freewebs","jimdo":r"jimdo","google sites":r"sites\.google\.com","yola":r"yola"}
NEWB={"wix":r"wix\.com|_wixCIDX|wixstatic","squarespace":r"squarespace","wordpress":r"wp-content|wp-includes","shopify":r"cdn\.shopify|myshopify","duda":r"dudaone|multiscreensite|dmcdn","webflow":r"webflow"}
BOOK=r"calendly|vagaro|schedulicity|booksy|mindbody|zocdoc|square\.site|squareup\.com/appointments|acuityscheduling|setmore|jane\.app|nexhealth|localmed|opencare|weave|book now|book online|schedule (an )?appointment|request (an )?appointment|order online|toasttab|doordash|ubereats|grubhub"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def fetch(url):
    t=time.time()
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html"})
    r=urllib.request.urlopen(req,timeout=15)
    body=r.read(600000).decode("utf-8","ignore")
    return r.status,r.geturl(),body,time.time()-t
def audit(site):
    out={"site":site}
    if not site: out["kind"]="none";return out
    host=urlparse(site if "://" in site else "http://"+site).netloc.lower()
    if any(s in host for s in SOCIAL): out["kind"]="social";out["host"]=host;return out
    url=site if "://" in site else "http://"+site
    try:
        st,final,body,el=fetch(url)
    except Exception as e:
        msg=str(e)
        # one retry over https
        if url.startswith("http://"):
            try: st,final,body,el=fetch("https://"+url[7:])
            except Exception as e2: out.update(kind="down",err=str(e2)[:90]);return out
        else: out.update(kind="down",err=msg[:90]);return out
    low=body.lower()
    out.update(kind="ok",status=st,final=final,https=final.startswith("https"),secs=round(el,1),kb=len(body)//1024)
    out["viewport"]=bool(re.search(r'<meta[^>]+name=["\']?viewport',low))
    yrs=[int(y) for y in re.findall(r'(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?((?:19|20)\d{2})',low)]
    out["year"]=max(yrs) if yrs else None
    out["old_builder"]=next((k for k,p in OLDB.items() if re.search(p,body,re.I)),None)
    out["builder"]=next((k for k,p in NEWB.items() if re.search(p,body,re.I)),None)
    out["title"]=bool(re.search(r"<title>\s*[^<\s]",low)); out["h1"]="<h1" in low
    imgs=re.findall(r"<img\b[^>]*>",low); out["imgs"]=len(imgs); out["noalt"]=sum(1 for i in imgs if not re.search(r'\balt=["\'][^"\']+',i))
    out["lang"]=bool(re.search(r"<html[^>]+lang=",low)); out["tel"]="tel:" in low
    out["booking"]=bool(re.search(BOOK,low)); out["form"]="<form" in low
    out["parked"]=bool(re.search(r"domain (is )?for sale|this domain|parked free|buy this domain|coming soon|under construction|account suspended",low)) and len(body)<40000
    out["flash"]=".swf" in low; out["tables"]=low.count("<table")>=4 and "viewport" not in low
    return out
if __name__=="__main__":
    src,dst=sys.argv[1],sys.argv[2]
    sites=sorted(set(json.load(open(src))))
    res={}
    with cf.ThreadPoolExecutor(12) as ex:
        for s,r in zip(sites,ex.map(audit,sites)): res[s]=r
    json.dump(res,open(dst,"w"))
    import collections;print(len(res),collections.Counter(r["kind"] for r in res.values()))
