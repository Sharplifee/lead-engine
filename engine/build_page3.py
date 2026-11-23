import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import json
L=json.load(open(LE_HOME+'/leads/leads3.json'))
import sys;sys.path.insert(0,LE_HOME+'/engine');from profiles import P as PROF
meta=json.load(open(LE_HOME+'/leads/meta.json'))
keep=['id','n','niche','addr','city','ph','web','gm','rt','rc','mi','weak','bg','choke','fit','prs','prox','score','sig','chk','pres','comp','tier','kind','vis','prof','angle','soc','home','alive','act','src']
import os
from PIL import Image
SH=LE_HOME+'/mshots/'
OUTD=LE_HOME+'/site/s/';os.makedirs(OUTD,exist_ok=True)
withshot=[l for l in L if l.get('shot')]
pos={}
TW,TH,C=200,866,10;RW=5
import shutil;shutil.rmtree(OUTD);os.makedirs(OUTD)
for k in range(0,len(withshot),C*RW):
    chunk=withshot[k:k+C*RW];sheet=Image.new('RGB',(TW*C,TH*RW),(240,240,240))
    for i,l in enumerate(chunk):
        im=Image.open(SH+l['shot']+'.jpg').convert('RGB').resize((TW,TH));sheet.paste(im,((i%C)*TW,(i//C)*TH))
        pos[l['id']]=[k//(C*RW),i%C,i//C]
    sheet.save(OUTD+f's{k//(C*RW)}.jpg',quality=60,optimize=True)
print('sheets',(len(withshot)+C*RW-1)//(C*RW))
data=[dict({k:l.get(k) for k in keep},sp=pos.get(l['id'])) for l in L]
html=r'''<title>Lead Engine</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{--bg:#fff;--panel:#f5f5f7;--ink:#1d1d1f;--muted:#6e6e73;--line:#e5e5ea;--line2:#d2d2d7;--accent:#0a7cff;--accent-soft:#0a7cff1a;--good:#28a745;--warn:#d9480f;--gold:#e08600;--seg:#e8e8ed;--seg-on:#fff;--shadow:0 1px 3px rgba(0,0,0,.1);--A:#28a745;--B:#e08600;--C:#8e8e93;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1c1c1e;--panel:#2c2c2e;--ink:#f5f5f7;--muted:#a1a1a6;--line:#38383a;--line2:#48484a;--accent:#0a84ff;--accent-soft:#0a84ff26;--good:#30d158;--warn:#ff9f0a;--gold:#ff9f0a;--seg:#3a3a3c;--seg-on:#636366;--shadow:0 1px 3px rgba(0,0,0,.5);--A:#30d158;--B:#ff9f0a;--C:#8e8e93;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1c1c1e;--panel:#2c2c2e;--ink:#f5f5f7;--muted:#a1a1a6;--line:#38383a;--line2:#48484a;--accent:#0a84ff;--accent-soft:#0a84ff26;--good:#30d158;--warn:#ff9f0a;--gold:#ff9f0a;--seg:#3a3a3c;--seg-on:#636366;--shadow:0 1px 3px rgba(0,0,0,.5);--A:#30d158;--B:#ff9f0a;--C:#8e8e93;color-scheme:dark}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);font:14px/1.45 var(--sans);-webkit-font-smoothing:antialiased}
button,input,select{font:inherit;color:inherit}
button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.app{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:18px 48px;display:grid;gap:16px}
h1{margin:0;font-size:24px;letter-spacing:-.02em}h1 span{font-size:14px;font-weight:400;color:var(--muted);margin-left:8px;letter-spacing:0}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}@media (max-width:760px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tile{background:var(--panel);border-radius:14px;padding:12px 14px;min-width:0}.tile span{font-size:12px;color:var(--muted);font-weight:600}.tile b{display:block;font-size:26px;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums}.tile small{font-size:12px;color:var(--muted)}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.seg{display:flex;background:var(--seg);border-radius:9px;padding:2px}.seg button{border:0;background:transparent;border-radius:7px;padding:5px 12px;font-size:13px;font-weight:500;cursor:pointer}.seg button[aria-pressed="true"]{background:var(--seg-on);box-shadow:var(--shadow)}
input[type=search],select{border:1px solid var(--line2);background:var(--bg);border-radius:8px;padding:6px 10px;font-size:13px;min-width:0}
input[type=search]{flex:1 1 200px}
.list{display:grid;gap:10px}
.lead{background:var(--panel);border-radius:14px;padding:14px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 14px;min-width:0}
.lead>*{min-width:0}
.lead h3{margin:0;font-size:16px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tier{font-size:11px;font-weight:800;color:#fff;border-radius:6px;padding:1px 7px}
.meta{font-size:12.5px;color:var(--muted)}
.score{text-align:right}.score b{font-size:22px;font-weight:800;font-variant-numeric:tabular-nums}.score small{display:block;font-size:11px;color:var(--muted)}
.sigs{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:12px;padding:2px 9px;border-radius:99px;background:var(--bg);border:1px solid var(--line2)}
.chip.hot{border-color:var(--warn);color:var(--warn)}
.chip.p{border-color:var(--gold);color:var(--gold)}
.chip.ck{border-color:#c2255c;color:#c2255c}
.layers{font-size:11px;color:var(--muted);text-align:right}
.prof{grid-column:2/-1;font-size:12px;color:var(--muted);margin:0}
.prof b{color:var(--ink);font-weight:600}
@media (max-width:640px){.prof,.why,.sigs,.acts{grid-column:1/-1}}
table.np{border-collapse:collapse;font-size:12px;width:100%}table.np td,table.np th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}.npwrap{overflow-x:auto}
.why{grid-column:1/-1;font-size:12.5px;color:var(--muted);margin:0}
.acts{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between}
.links{display:flex;gap:12px;flex-wrap:wrap;font-size:13px}.links a{color:var(--accent);text-decoration:none}
.st{display:flex;background:var(--seg);border-radius:8px;padding:2px}.st button{border:0;background:transparent;border-radius:6px;padding:3px 9px;font-size:12px;cursor:pointer}.st button[aria-pressed="true"]{background:var(--seg-on);box-shadow:var(--shadow);font-weight:600}
.more{justify-self:center;border:1px solid var(--line2);background:var(--bg);border-radius:99px;padding:6px 16px;cursor:pointer}
details{background:var(--panel);border-radius:14px;padding:14px}details summary{cursor:pointer;font-weight:700}details p,details li{color:var(--muted);font-size:13px;max-width:80ch}
.note{font-size:11.5px;color:var(--muted)}
.lead{grid-template-columns:108px minmax(0,1fr) auto!important}
.thumb{grid-row:span 3;width:100px;height:217px;border-radius:12px;border:2px solid var(--line2);background-color:var(--bg);background-repeat:no-repeat;cursor:zoom-in;padding:0}
.nothumb{grid-row:span 3;width:100px;height:217px;border-radius:8px;border:1px dashed var(--line2);display:grid;place-content:center;font-size:11.5px;color:var(--muted);text-align:center;padding:6px}
.look{font-size:12.5px;font-weight:600}
.look.r{color:var(--warn)}.look.m{color:var(--gold)}.look.s{color:var(--good)}
@media (max-width:640px){.lead{grid-template-columns:100px minmax(0,1fr)!important}.lead .score{grid-column:2}}
dialog{border:0;border-radius:14px;padding:0;max-width:min(92vw,340px);max-height:90vh;overflow:auto;background:var(--bg);color:var(--ink)}
dialog::backdrop{background:rgba(0,0,0,.6)}
dialog .big{width:300px;height:1299px;background-repeat:no-repeat;margin:0 auto}
dialog p{margin:0;padding:10px 14px;font-size:13px}
.pres{grid-column:2/-1;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:12.5px}.pres a{color:var(--accent);text-decoration:none}
.home{font-weight:600}.alive{font-size:11px;font-weight:700;border-radius:6px;padding:1px 7px;color:#fff}.alive.active{background:var(--good)}.alive.steady{background:var(--gold)}.alive.dormant,.alive.paused,.alive.closed{background:var(--warn)}.alive.unchecked{background:var(--C)}
@media (max-width:640px){.pres{grid-column:1/-1}}
.kpi{background:var(--panel);border-radius:16px;padding:16px;display:grid;gap:10px}.kpi h2{margin:0;font-size:17px}.kpi .row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}@media (max-width:760px){.kpi .row{grid-template-columns:repeat(2,minmax(0,1fr))}}
.kpi .row div{background:var(--bg);border-radius:12px;padding:10px 12px;min-width:0}.kpi .row span{font-size:12px;color:var(--muted);font-weight:600}.kpi .row b{display:block;font-size:22px;font-weight:800;font-variant-numeric:tabular-nums}.kpi .row small{font-size:11.5px;color:var(--muted)}
.meter{height:10px;border-radius:99px;background:var(--seg);overflow:hidden}.meter i{display:block;height:100%;background:var(--good);border-radius:99px}
.kpi p{margin:0;font-size:12.5px;color:var(--muted)}
.today{background:linear-gradient(135deg,var(--panel),var(--accent-soft));border-radius:16px;padding:16px}
.today h2{margin:0 0 4px;font-size:20px}.today p{margin:0;color:var(--muted);font-size:13px}
</style>
<div class="app">
<div><h1>Lead Engine<span id="sub"></span></h1></div>
<section class="tiles" id="tiles"></section>
<section class="kpi" id="kpi"></section>
<section class="today"><h2 id="th"></h2><p id="tp"></p></section>
<div class="bar">
  <div class="seg" role="group" aria-label="View" id="views"><button data-v="today" aria-pressed="true">Today's 30</button><button data-v="intake">Intake (60)</button><button data-v="all">All leads</button></div>
  <input type="search" id="q" placeholder="Search name, niche, city" aria-label="Search">
  <select id="tierSel" aria-label="Tier"><option value="AB">Tier A + B</option><option value="A">Tier A</option><option value="B">Tier B</option><option value="C">Tier C</option><option value="ALL">All tiers</option></select>
  <select id="nicheSel" aria-label="Niche"><option value="">All niches</option></select>
  <select id="citySel" aria-label="City"><option value="">All cities</option></select>
  <select id="stSel" aria-label="Status"><option value="open">Not sent yet</option><option value="">Any status</option><option value="built">Built</option><option value="sent">Sent</option><option value="replied">Replied</option><option value="sold">Sold</option><option value="pass">Pass</option></select>
  <select id="lookSel" aria-label="Look"><option value="">Any look</option><option value="redesign">Looks outdated on phones</option><option value="maybe">Looks so-so on phones</option><option value="skip">Looks modern on phones</option><option value="none">Not seen</option></select>
  <select id="homeSel" aria-label="Online presence"><option value="">Any presence</option><option>Facebook is their website</option><option>Instagram is their website</option><option>No real home online</option><option>Website</option></select>
  <select id="sortSel" aria-label="Sort"><option value="mi">Closest to 84097 first</option><option value="score">Highest score first</option></select>
</div>
<p class="note" id="count"></p>
<section class="list" id="list" aria-label="Leads"></section>
<button class="more" id="more" hidden>Show 50 more</button>
<details><summary>How the engine finds and ranks leads</summary>
<ol>
<li><b>Discover.</b> Google Maps listings for 37 niches where a website drives calls or bookings, starting in Orem and moving outward ring by ring: Provo, Lindon, Pleasant Grove, then American Fork, Lehi, Springville and Spanish Fork. Chains and franchises are removed, since their sites are corporate.</li>
<li><b>Verify.</b> Every listed website is loaded and checked: does it load at all, is it secure, does it work on a phone, how old is it, what builder is it on, can you tap to call or book, do images have alt text (ADA exposure). Sites that failed were checked a second time before being marked broken. Sites that block automated checks are marked "couldn't check", not broken.</li>
<li><b>Look, phone first.</b> Every working site is opened as an iPhone and its top two screens are photographed. The page also measures whether it scrolls sideways (a desktop page squeezed onto a phone) and whether there is a tap-to-call link near the top. An AI vision model then gives each phone screenshot the 2 to 3 second look you would, judging design, readability, tap-friendly buttons, an obvious way to call or book, and whether it actually fits the phone. It returns <i>outdated</i>, <i>so-so</i> or <i>modern</i>, a 1 to 10 "dated" rating and a one-line reason. Outdated adds up to 30 to Need, so-so adds 5, modern takes 15 off, and sideways scrolling adds 10. Tap any thumbnail to see both screens.</li>
<li><b>Business type and how it wins customers.</b> Every niche has a profile: how new customers find it, how often they come back, how much the website decides who gets the business, and how much looks matter. Nail, lash, hair, med spa, tattoo, boutique and bakery clients choose by looks and share links with friends, so the brand has to be beautiful; trades and professional services need to look credible and get a tap-to-call or quote fast. See the table below.</li>
<li><b>Choke points.</b> Each site is read for how a customer actually books, orders or calls: booking that sends them off to Vagaro, GlossGenius, Square or another app; more than one booking tool; "call to book" or DM-to-book; restaurant orders that only run through DoorDash or Grubhub; shops and florists with no way to order online; and urgent trades with no tap-to-call. Missing-booking calls need both the code check and the screenshot to agree.</li>
<li><b>Brand gap.</b> The screenshot judge also rates brand fit for that kind of business, 1 to 10. The gap between that and how much looks matter in the niche becomes the brand score.</li>
<li><b>Score, out of 100.</b> Site weakness up to 40, brand gap up to 10, choke points up to 15, business fit up to 20, pressure up to 5, and pride lift up to 10: how big and exciting the upgrade will feel to the owner, from how dated their site looks now, how much looks matter in their niche, and how proud they are of their reputation. Distance is not scored; 84097 is only where the daily route starts. Tiers are about quality, not quantity. Tier A needs a score of 55+ and all three: proof the site is bad (judged outdated on a phone, or no site, social page only, broken, parked or disabled), a healthy business (10+ Google reviews at 4.0 stars or better), and a niche where the website really matters. Tier B has the proof but a weaker business signal, or a so-so site with a big choke point in a strong business. Everything else is tier C. Each day the intake holds the next 60 strongest open leads, and today's 30 are the top half.</li>
<li><b>Where they live online.</b> For every tier A and B lead the engine reads the business's own website for its Instagram, Facebook and TikTok links, then runs a Google search for "name city Utah instagram OR facebook" and keeps only results whose handle or title matches the business name. Instagram profiles are opened for followers, post count and the date of the last post, so a tattoo shop whose Instagram is effectively its website shows up as "Instagram is their website." Business pages only: owners' personal profiles are not searched or collected.</li>
<li><b>Still open and still trying.</b> Each lead's Google listing is pulled fresh: permanently or temporarily closed, whether hours are posted, and the dates of the newest reviews. Active means a review in the last 120 days or a post in the last 45; steady means within a year or six months; gone quiet means neither. Closed leads drop to tier C, gone-quiet and temporarily closed leads drop one tier, and an active social-only business with a real Instagram following moves up to tier A.</li>
<li><b>Pressure.</b> Pressure counts an unclaimed Google profile, very few reviews, a low rating and almost no photos.</li>
<li><b>Pitch.</b> Each lead names up to three nearby businesses in the same niche whose sites already pass, so your pitch is "they already have this; you don't."</li>
<li><b>Track.</b> Mark each lead Built, Sent, Sold or Pass. Today's 30 are the strongest open leads, tier A first, by score. 84097 is only where the search started.</li>
</ol>
<div class="npwrap"><table class="np"><tr><th>Niche</th><th>Found through</th><th>Comes back</th><th>Website matters</th><th>Looks matter</th></tr><tr><td>HVAC</td><td>Urgent Google search, Maps</td><td>seasonal service</td><td>9/10</td><td>4/10</td></tr><tr><td>accountant</td><td>Referrals, Google search</td><td>yearly, for years</td><td>6/10</td><td>5/10</td></tr><tr><td>auto body shop</td><td>Google search, insurance referrals</td><td>rare</td><td>8/10</td><td>5/10</td></tr><tr><td>auto detailing</td><td>Instagram, Google, referrals</td><td>monthly or seasonal</td><td>7/10</td><td>9/10</td></tr><tr><td>auto repair</td><td>Google Maps, referrals</td><td>every few months</td><td>8/10</td><td>4/10</td></tr><tr><td>bakery</td><td>Instagram, Google Maps, word of mouth</td><td>weekly to monthly</td><td>7/10</td><td>9/10</td></tr><tr><td>barber shop</td><td>Google Maps, walk-by, Instagram</td><td>every 2-4 weeks</td><td>7/10</td><td>8/10</td></tr><tr><td>chiropractor</td><td>Google search, referrals</td><td>weekly to monthly</td><td>9/10</td><td>6/10</td></tr><tr><td>cleaning service</td><td>Google search, referrals</td><td>weekly to monthly</td><td>8/10</td><td>6/10</td></tr><tr><td>clothing boutique</td><td>Instagram, walk-by</td><td>monthly</td><td>8/10</td><td>10/10</td></tr><tr><td>coffee shop</td><td>Google Maps, Instagram, walk-by</td><td>several times a week</td><td>6/10</td><td>9/10</td></tr><tr><td>dance studio</td><td>Referrals, Instagram, Google</td><td>weekly classes</td><td>7/10</td><td>8/10</td></tr><tr><td>daycare</td><td>Google search, referrals</td><td>daily, for years</td><td>8/10</td><td>7/10</td></tr><tr><td>dentist</td><td>Google search, insurance lists, referrals</td><td>twice a year, for years</td><td>9/10</td><td>7/10</td></tr><tr><td>electrician</td><td>Google search, referrals</td><td>as needed</td><td>8/10</td><td>4/10</td></tr><tr><td>florist</td><td>Google search, delivery directories</td><td>holidays and events</td><td>9/10</td><td>9/10</td></tr><tr><td>gym</td><td>Google Maps, Instagram, drive-by</td><td>several times a week</td><td>7/10</td><td>8/10</td></tr><tr><td>hair salon</td><td>Instagram, referrals, Google Maps</td><td>every 4-8 weeks</td><td>8/10</td><td>9/10</td></tr><tr><td>insurance agency</td><td>Referrals, Google search</td><td>yearly renewals</td><td>6/10</td><td>5/10</td></tr><tr><td>jewelry store</td><td>Google search, Instagram, referrals</td><td>milestones</td><td>8/10</td><td>10/10</td></tr><tr><td>landscaping</td><td>Google search, referrals, yard signs</td><td>weekly in season</td><td>7/10</td><td>7/10</td></tr><tr><td>law firm</td><td>Google search, referrals</td><td>rare, high stakes</td><td>9/10</td><td>6/10</td></tr><tr><td>martial arts</td><td>Google search, referrals</td><td>weekly classes</td><td>7/10</td><td>6/10</td></tr><tr><td>massage therapy</td><td>Google search, Maps, referrals</td><td>monthly</td><td>8/10</td><td>7/10</td></tr><tr><td>med spa</td><td>Instagram, Google search, referrals</td><td>every 1-3 months</td><td>9/10</td><td>10/10</td></tr><tr><td>nail salon</td><td>Instagram, friends' recommendations, Google Maps</td><td>every 2-3 weeks</td><td>8/10</td><td>10/10</td></tr><tr><td>optometrist</td><td>Google search, insurance lists</td><td>yearly</td><td>8/10</td><td>7/10</td></tr><tr><td>pest control</td><td>Urgent Google search</td><td>quarterly plans</td><td>8/10</td><td>4/10</td></tr><tr><td>pet grooming</td><td>Google Maps, Instagram, referrals</td><td>every 4-8 weeks</td><td>7/10</td><td>8/10</td></tr><tr><td>photographer</td><td>Instagram, Google, referrals</td><td>occasional</td><td>9/10</td><td>10/10</td></tr><tr><td>physical therapy</td><td>Doctor referrals, Google search</td><td>weekly during care</td><td>8/10</td><td>6/10</td></tr><tr><td>plumber</td><td>Urgent Google search, Maps</td><td>as needed</td><td>9/10</td><td>4/10</td></tr><tr><td>restaurant</td><td>Google Maps, Instagram, delivery apps</td><td>weekly to monthly</td><td>7/10</td><td>8/10</td></tr><tr><td>roofing contractor</td><td>Google search, door-knocking, referrals</td><td>rare, big ticket</td><td>8/10</td><td>6/10</td></tr><tr><td>tattoo shop</td><td>Instagram, referrals, Google</td><td>occasional</td><td>7/10</td><td>9/10</td></tr><tr><td>tire shop</td><td>Google Maps, drive-by</td><td>seasonal</td><td>6/10</td><td>3/10</td></tr><tr><td>veterinarian</td><td>Google search, referrals</td><td>1-3 times a year, for years</td><td>8/10</td><td>6/10</td></tr></table></div>
<p>"No website on Google" means Google lists none. Search their name once before building, since some have a site Google doesn't show.</p>
</details>
<dialog id="zoom"><div class="big" id="zbig"></div><p id="zcap"></p></dialog>
<p class="note">Business data from Google Maps, collected '''+meta['date']+r'''. Website checks run the same day.</p>
</div>
<script id="data" type="application/json">'''+json.dumps(data,separators=(',',':')).replace('</','<\\/')+r'''</script>
<script>
const $=id=>document.getElementById(id);
const D=JSON.parse($("data").textContent);
const META='''+json.dumps(meta)+r''';
const ST={};let db=null;
try{Object.assign(ST,JSON.parse(localStorage.getItem("le_status")||"{}"))}catch(e){}
const saveLocal=()=>{try{localStorage.setItem("le_status",JSON.stringify(ST))}catch(e){}};
let view="today",shown=50;
const esc=s=>String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");
const LABEL={"":"New",built:"Built",sent:"Sent",replied:"Replied",sold:"Sold",pass:"Pass"};
const EV={};try{Object.assign(EV,JSON.parse(localStorage.getItem("le_ev")||"{}"))}catch(e){}
const saveEv=()=>{try{localStorage.setItem("le_ev",JSON.stringify(EV))}catch(e){}};
const ALV={active:"Active",steady:"Steady",dormant:"Gone quiet",paused:"Temporarily closed",closed:"Closed",unchecked:"Not checked"};
const kf=n=>n==null?"":n>=1000?(n/1000).toFixed(n>=10000?0:1)+"k":String(n);
function filt(){const q=$("q").value.toLowerCase().trim(),t=$("tierSel").value,n=$("nicheSel").value,c=$("citySel").value,s=$("stSel").value;
  const lk=$("lookSel").value,hm=$("homeSel").value;
  let r=D.filter(l=>(!hm||l.home===hm)&&(!lk||(lk==="none"?!l.vis||!l.sp:l.vis&&l.vis.v===lk))&&(t==="ALL"||t.includes(l.tier))&&(!n||l.niche===n)&&(!c||l.city===c)&&(!q||(l.n+" "+l.niche+" "+(l.city||"")).toLowerCase().includes(q)));
  r=r.filter(l=>{const st=ST[l.id]||"";return s===""?true:s==="open"?!(st==="sent"||st==="replied"||st==="sold"||st==="pass"):st===s});
  r.sort($("sortSel").value==="mi"?(a,b)=>(a.mi??99)-(b.mi??99)||b.score-a.score:(a,b)=>b.score-a.score||a.mi-b.mi);return r}
const open_=l=>!["built","sent","replied","sold","pass"].includes(ST[l.id]||"");
function intake(){return D.filter(l=>l.tier!=="C"&&open_(l)).sort((a,b)=>(a.tier>b.tier)-(a.tier<b.tier)||b.score-a.score).slice(0,60)}
function todays(){return intake().slice(0,30)}
const bg=(sp,w=100)=>{const h=w*866/200;return `background-image:url(s/s${sp[0]}.jpg);background-size:${w*10}px ${h*5}px;background-position:-${sp[1]*w}px -${sp[2]*h}px`};
function pres(l){if(!l.home&&!l.alive)return "";const S=l.soc||{},b=[];
  if(l.alive)b.push(`<span class="alive ${l.alive}">${ALV[l.alive]}</span>`);
  if(l.home)b.push(`<span class="home">${esc(l.home)}</span>`);
  if(S.ig){const g=S.ig;b.push(`<a href="https://www.instagram.com/${encodeURIComponent(g.h)}/" target="_blank" rel="noopener">Instagram @${esc(g.h)}</a>${g.f!=null?` ${kf(g.f)} followers`:""}${g.d!=null?` · posted ${g.d}d ago`:""}`)}
  if(S.fb){b.push(`<a href="https://www.facebook.com/${encodeURIComponent(S.fb.h)}" target="_blank" rel="noopener">Facebook page</a>${S.fb.f!=null?` ${kf(S.fb.f)} followers`:""}`)}
  if(S.tt)b.push(`<a href="https://www.tiktok.com/@${encodeURIComponent(S.tt.h)}" target="_blank" rel="noopener">TikTok</a>`);
  if(l.act)b.push(`<span class="meta">${esc(l.act)}</span>`);
  return `<div class="pres">${b.join("")}</div>`}
function card(l){const st=ST[l.id]||"";
  const sig=l.sig.map(([k,t])=>`<span class="chip${/broken|No website|Social|Parked|mobile/.test(k)?" hot":""}" title="${esc(t)}">${esc(k)}</span>`).join("")+l.chk.map(c=>`<span class="chip ck" title="Choke point">${esc(c)}</span>`).join("")+l.pres.map(p=>`<span class="chip p">${esc(p)}</span>`).join("");
  const why=[l.vis&&l.vis.r?l.vis.r+".":"",l.vis&&l.vis.bn?"Brand: "+l.vis.bn+(/[.!]$/.test(l.vis.bn)?"":"."):""].filter(Boolean).join(" ")||(l.sig.length?l.sig[0][1]:"");
  const th=l.sp?`<button class="thumb" data-z="${esc(l.id)}" aria-label="Enlarge phone screenshot of ${esc(l.n)}" style="${bg(l.sp)}"></button>`:`<div class="nothumb">${l.web?"No screenshot":"No website to show"}</div>`;
  const lk=l.vis&&l.vis.v!=="unseen"?`<div class="look ${l.vis.v[0]}">${l.vis.v==="redesign"?"Looks outdated on phones":l.vis.v==="maybe"?"Looks so-so on phones":"Looks modern on phones"} · ${l.vis.d}/10 dated</div>`:"";
  return `<article class="lead" data-id="${esc(l.id)}">${th}<div><h3><span class="tier" style="background:var(--${l.tier})">${l.tier}</span>${esc(l.n)}</h3>${lk}<div class="meta">${esc(l.niche)} · ${esc(l.city||"")} · ${l.mi!=null?l.mi+" mi · ":""}${l.src==="bots"?"new from bot sweep · ":""}${l.rc?`${l.rt}★ (${l.rc})`:"no reviews"}${l.ph?" · "+esc(l.ph):""}</div></div>
   <div class="score"><b>${l.score}</b><div class="layers">site ${l.weak} · brand ${l.bg} · choke ${l.choke}<br>fit ${l.fit} · pressure ${l.prs} · pride lift ${l.prox}</div></div>
   ${pres(l)}
   <p class="prof"><b>Why it matters:</b> ${esc(l.angle)} <br>Found through ${esc(l.prof.found)} · comes back ${esc(l.prof.repeat)} · website matters ${l.prof.web}/10 · looks matter ${l.prof.look}/10</p>
   <div class="sigs">${sig||'<span class="chip">No major issues found</span>'}</div>
   ${why?`<p class="why">${esc(why)}${l.comp.length?` Nearby with working sites: ${l.comp.map(esc).join(", ")}.`:""}</p>`:l.comp.length?`<p class="why">Nearby with working sites: ${l.comp.map(esc).join(", ")}.</p>`:""}
   <div class="acts"><div class="links">${l.web?`<a href="${esc(/^https?:/.test(l.web)?l.web:"http://"+l.web)}" target="_blank" rel="noopener">Their site</a>`:""}${l.gm?`<a href="${esc(l.gm)}" target="_blank" rel="noopener">Google Maps</a>`:""}<span class="meta">${esc(l.addr)}</span></div>
   <div class="st" role="group" aria-label="Status">${["","built","sent","replied","sold","pass"].map(s=>`<button data-s="${s}" aria-pressed="${st===s}">${LABEL[s]}</button>`).join("")}</div></div></article>`}
function weekStart(){const n=new Date(new Date().toLocaleString("en-US",{timeZone:"America/Denver"}));const d=(n.getDay()+6)%7;n.setHours(0,0,0,0);n.setDate(n.getDate()-d);return n}
function kpi(){const w0=weekStart(),now=new Date(new Date().toLocaleString("en-US",{timeZone:"America/Denver"}));
  const inW=t=>{if(!t)return false;const d=new Date(new Date(t).toLocaleString("en-US",{timeZone:"America/Denver"}));return d>=w0};
  const cnt=k=>Object.values(EV).filter(e=>inW(e[k])).length,sent=cnt("sent"),rep=cnt("replied"),sold=cnt("sold");
  const day=Math.min(7,Math.floor((now-w0)/864e5)+1),pace=Math.round(5*day/7*10)/10;
  const left=Math.max(0,5-sold),sendsLeft=Math.max(0,210-sent),need=sendsLeft?Math.round(left/sendsLeft*1000)/10:0;
  const allSent=Object.values(EV).filter(e=>e.sent).length,allSold=Object.values(EV).filter(e=>e.sold).length,allRep=Object.values(EV).filter(e=>e.replied).length;
  $("kpi").innerHTML=`<h2>Pre-sales scorecard · this week (Mon–Sun)</h2>
  <div class="meter" role="img" aria-label="${sold} of 5 sales this week"><i style="width:${Math.min(100,sold/5*100)}%"></i></div>
  <div class="row"><div><span>Sales this week</span><b>${sold} / 5</b><small>minimum · pace today ${pace}</small></div>
  <div><span>Sent this week</span><b>${sent} / 210</b><small>30 a day</small></div>
  <div><span>Replies this week</span><b>${rep}</b><small>${sent?Math.round(rep/sent*100):0}% of sent</small></div>
  <div><span>Close rate needed</span><b>${need}%</b><small>on the ${sendsLeft} sends left this week</small></div>
  <div><span>All time</span><b>${allSold} sold</b><small>${allSent} sent · ${allRep} replied${allSent?` · ${Math.round(allSold/allSent*1000)/10}% close`:""}</small></div></div>
  <p>The floor is 5 sales a week. At 210 sends that takes a 2.4% close, and the Execution Calendar plan assumes about 25%, so 5 is the minimum, not the goal. Mark Sent, Replied and Sold on each lead and this updates.</p>`}
function render(){kpi();
  const ab=D.filter(l=>l.tier!=="C").length,a=D.filter(l=>l.tier==="A").length,c=(s)=>Object.values(ST).filter(v=>v===s).length;
  $("sub").textContent=`84097 outward · ${D.length.toLocaleString()} businesses checked`;
  $("tiles").innerHTML=`<div class="tile"><span>Qualified leads (A + B)</span><b>${ab}</b><small>${a} tier A</small></div>
   <div class="tile"><span>Days of tier A at 30 a day</span><b>${Math.floor(D.filter(l=>l.tier==="A"&&open_(l)).length/30)}</b><small>then the next scrape is due</small></div>
   <div class="tile"><span>All businesses scored</span><b>${(D.length/META.need1).toFixed(1)}×</b><small>${D.length.toLocaleString()} incl. tier C</small></div>
   <div class="tile"><span>Your progress</span><b>${c("sent")+c("sold")}</b><small>sent · ${c("sold")} sold · ${c("built")} built</small></div>`;
  const T=todays(),I=intake(),poolA=D.filter(l=>l.tier==="A"&&open_(l)).length;$("th").textContent=`Today's 30: build today, send tomorrow`;$("tp").textContent=T.length?`The 30 strongest of the next ${I.length} leads in the intake, ranked by score. Mark each Built when it's done and Sent once it goes out. ${poolA} tier A leads are left, about ${Math.floor(poolA/30)} days at 30 a day.`:"The intake is empty. Time to run a new scrape.";
  const rows=view==="today"?T:view==="intake"?I:filt();
  $("count").textContent=view==="all"?`${rows.length.toLocaleString()} leads match`:view==="intake"?"The next 60 strongest open leads; the top 30 are today's picks. Mark Pass on any you'd skip and the next one moves up.":"";
  $("list").innerHTML=rows.slice(0,view==="all"?shown:60).map(card).join("");
  $("more").hidden=view!=="all"||rows.length<=shown;
  document.querySelectorAll(".bar select,#q").forEach(el=>el.disabled=view!=="all");
}
$("list").addEventListener("click",e=>{const z=e.target.closest("[data-z]");if(z){const l=D.find(x=>x.id===z.dataset.z);$("zbig").style.cssText=bg(l.sp,300);$("zcap").textContent=`${l.n}: ${l.vis?l.vis.r:""}`;$("zoom").showModal();return}const b=e.target.closest("[data-s]");if(!b)return;const id=b.closest(".lead").dataset.id,s=b.dataset.s;if(s)ST[id]=s;else delete ST[id];saveLocal();const ev=EV[id]=EV[id]||{};const now=Date.now();if(s==="sent"&&!ev.sent)ev.sent=now;if(s==="replied"){ev.sent=ev.sent||now;ev.replied=ev.replied||now}if(s==="sold"){ev.sent=ev.sent||now;ev.sold=ev.sold||now}if(!s||s==="built"||s==="pass"){delete EV[id]}saveEv();
  if(db){db.collection("leads").doc(id.replace(/[^A-Za-z0-9_-]/g,"_")).set({id,s:s||"",at:Date.now(),ev:EV[id]||{}}).catch(()=>{})}render()});
document.querySelectorAll("#views button").forEach(b=>b.onclick=()=>{view=b.dataset.v;document.querySelectorAll("#views button").forEach(x=>x.setAttribute("aria-pressed",x===b));shown=50;render()});
["q","tierSel","nicheSel","citySel","stSel","lookSel","homeSel","sortSel"].forEach(id=>$(id).addEventListener("input",()=>{shown=50;render()}));
$("more").onclick=()=>{shown+=50;render()};
[...new Set(D.map(l=>l.niche))].sort().forEach(n=>$("nicheSel").insertAdjacentHTML("beforeend",`<option>${esc(n)}</option>`));
[...new Set(D.map(l=>l.city).filter(Boolean))].sort().forEach(n=>$("citySel").insertAdjacentHTML("beforeend",`<option>${esc(n)}</option>`));
$("zoom").addEventListener("click",()=>$("zoom").close());
render();
(async()=>{try{if(!window.claude||!claude.use)return;db=await claude.use("db");if(!db)return;
  const t=setTimeout(()=>{},10000);
  db.collection("leads").onSnapshot(s=>{clearTimeout(t);s.docs.forEach(d=>{const v=d.data();if(v&&v.id){if(v.s)ST[v.id]=v.s;else delete ST[v.id];if(v.ev&&Object.keys(v.ev).length)EV[v.id]=v.ev;else delete EV[v.id]}});saveLocal();saveEv();render()},()=>clearTimeout(t))}catch(e){}})();
</script>
'''
open(LE_HOME+'/site/index.html','w').write(html)
print(len(html)//1024,'KB')
