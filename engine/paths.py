import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Customer-path check: how a visitor books, orders, buys or contacts, and where they get sent."""
import json,re,sys,concurrent.futures as cf,urllib.request
from urllib.parse import urlparse,urljoin
S=LE_HOME+'/'
A=json.load(open(S+'leads/audit.json'))
BOOK={'vagaro':'Vagaro','booksy':'Booksy','glossgenius':'GlossGenius','styleseat':'StyleSeat','schedulicity':'Schedulicity','mindbodyonline':'Mindbody','mindbody':'Mindbody','fresha':'Fresha','squareup.com/appointments':'Square','square.site':'Square','book.squareup':'Square','calendly':'Calendly','acuityscheduling':'Acuity','setmore':'Setmore','janeapp':'Jane','jane.app':'Jane','zocdoc':'Zocdoc','nexhealth':'NexHealth','localmed':'LocalMed','opencare':'Opencare','solutionreach':'Solutionreach','weave':'Weave','housecallpro':'Housecall Pro','jobber':'Jobber','servicetitan':'ServiceTitan','getjobber':'Jobber','opentable':'OpenTable','resy':'Resy','tock':'Tock','yelp.com/reservations':'Yelp','genbook':'Genbook','simplybook':'SimplyBook','zenoti':'Zenoti','boulevard':'Boulevard','joinblvd':'Boulevard','phorest':'Phorest','gettimely':'Timely','salonbiz':'SalonBiz','meevo':'Meevo','petexec':'PetExec','gingr':'Gingr','petsbe':'Petsbe','daysmart':'DaySmart','appointy':'Appointy','10to8':'10to8','zenmaid':'ZenMaid','thumbtack':'Thumbtack'}
ORDER={'toasttab':'Toast','doordash':'DoorDash','ubereats':'Uber Eats','grubhub':'Grubhub','order.online':'Online ordering','chownow':'ChowNow','clover.com/online':'Clover','popmenu':'Popmenu','slicelife':'Slice','menufy':'Menufy','beyondmenu':'BeyondMenu','olo.com':'Olo'}
SHOP={'cdn.shopify':'Shopify','myshopify':'Shopify','woocommerce':'WooCommerce','bigcommerce':'BigCommerce','square.site':'Square Online','ecwid':'Ecwid','etsy.com':'Etsy','stripe.com':'Stripe','paypal.com':'PayPal'}
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
def run(site):
    v=A.get(site,{})
    if v.get('kind')!='ok':return site,None
    try:
        u=v.get('final') or (site if '://' in site else 'http://'+site)
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=15)
        html=r.read(800000).decode('utf-8','ignore');base=r.geturl()
    except Exception as e:return site,{'err':str(e)[:60]}
    low=html.lower();own=urlparse(base).netloc.replace('www.','')
    hrefs=re.findall(r'href=["\']([^"\'#]+)',html,re.I);srcs=re.findall(r'<(?:iframe|script)[^>]+src=["\']([^"\']+)',html,re.I)
    def norm(x):
        p=urlparse(urljoin(base,x));return (p.netloc.lower().replace('www.','')+p.path.lower()) if p.netloc and p.netloc.replace('www.','')!=own else ''
    def hits(table,pool):
        ns=[norm(x) for x in pool]
        return sorted({name for k,name in table.items() for x in ns if x and (x.startswith(k) or ('.'+k) in x or ('/'+k) in x)})
    linked_book=hits(BOOK,hrefs);embed_book=hits(BOOK,srcs)
    out={'book_link':linked_book,'book_embed':embed_book,'order':hits(ORDER,hrefs+srcs),'shop':sorted(set(hits(SHOP,hrefs+srcs)+(['Shopify'] if 'cdn.shopify.com' in low else [])+(['WooCommerce'] if 'woocommerce' in low else []))),
         'social':sorted({d for d in ['facebook','instagram','tiktok','yelp','linktr.ee'] if any(d in h.lower() for h in hrefs)}),
         'call_to_book':bool(re.search(r'call (us )?(today )?to (book|schedule|make an appointment)|call for (an )?appointment',low)),
         'dm_to_book':bool(re.search(r'(dm|message) (us|me) to book|book (via|through|on) instagram|text (us|me) to book',low)),
         'form':'<form' in low,'pages':len({urlparse(urljoin(base,h)).path for h in hrefs if urlparse(urljoin(base,h)).netloc.replace('www.','')==own})}
    out['book_hosts']=sorted(set(linked_book+embed_book))
    return site,out
sites=[s for s,v in A.items() if v.get('kind')=='ok']
res={}
with cf.ThreadPoolExecutor(14) as ex:
    for s,o in ex.map(run,sites):res[s]=o
json.dump(res,open(S+'leads/paths.json','w'))
import collections
ok=[o for o in res.values() if o and 'err' not in o]
print(len(ok),'booking providers',collections.Counter(b for o in ok for b in o['book_hosts']).most_common(12))
print('bounce-only (linked not embedded)',sum(1 for o in ok if o['book_link'] and not o['book_embed']),'embedded',sum(1 for o in ok if o['book_embed']),'multi-provider',sum(1 for o in ok if len(o['book_hosts'])>1))
print('order',collections.Counter(b for o in ok for b in o['order']).most_common(6),'call-to-book',sum(o['call_to_book'] for o in ok),'dm',sum(o['dm_to_book'] for o in ok))
