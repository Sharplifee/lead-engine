import os as _os
LE_HOME=_os.environ.get('LE_HOME',_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""Presence map + alive check on top of score2 output -> leads3.json. Business pages only; no personal profiles."""
import json,os,datetime as dt,collections
S=LE_HOME+'/'
L=json.load(open(S+'leads/leads2.json'))
M=json.load(open(S+'social/merged.json')) if os.path.exists(S+'social/merged.json') else {}
A=json.load(open(S+'social/activity.json')) if os.path.exists(S+'social/activity.json') else {}
IG=json.load(open(S+'social/ig.json')) if os.path.exists(S+'social/ig.json') else {}
FB=json.load(open(S+'social/fb.json')) if os.path.exists(S+'social/fb.json') else {}
today=dt.date(2026,11,22)
def ago(d):return (today-dt.date.fromisoformat(d[:10])).days if d else None
c=collections.Counter()
for l in L:
    if l['tier']=='C':continue
    m=M.get(l['id'],{});a=A.get(l['id']);soc={}
    if m.get('ig'):
        p=IG.get(m['ig'].lower(),{});soc['ig']={'h':m['ig'],'f':p.get('f'),'n':p.get('n'),'d':ago(p.get('last')),'bio':p.get('bio')}
    if m.get('fb') and not (FB.get(m['fb']) or FB.get(m['fb'].lower()) or {}).get('personal'):
        p=FB.get(m['fb']) or FB.get(m['fb'].lower()) or {};soc['fb']={'h':m['fb'],'f':p.get('f'),'d':ago(p.get('last'))}
    if m.get('tt'):soc['tt']={'h':m['tt']}
    l['soc']=soc
    # where they actually live online
    igd=(soc.get('ig') or {}).get('d');igf=(soc.get('ig') or {}).get('f') or 0
    if l['kind'] in('none','social') and igd is not None and igd<=60 and igf>=300:home='Instagram is their website'
    elif l['kind'] in('none','social') and soc.get('fb'):home='Facebook is their website'
    elif l['kind'] in('none','social'):home='No real home online'
    else:home='Website'
    l['home']=home
    # alive & consistent
    rd=a['days'] if a else None;postd=min([x for x in [igd,(soc.get('fb') or {}).get('d')] if x is not None],default=None)
    if a and a['closed']=='perm':st='closed'
    elif a and a['closed']=='temp':st='paused'
    elif (rd is not None and rd<=120) or (postd is not None and postd<=45):st='active'
    elif (rd is not None and rd<=365) or (postd is not None and postd<=180):st='steady'
    elif a is None:st='unchecked'
    else:st='dormant'
    l['alive']=st
    bits=[]
    if rd is not None:bits.append(f"last Google review {rd}d ago")
    elif a:bits.append("no recent Google reviews")
    if igd is not None:bits.append(f"last Instagram post {igd}d ago")
    if a and not a['hours']:bits.append("no hours listed")
    l['act']=", ".join(bits)
    old=l['tier']
    if st in('closed',):l['tier']='C'
    elif st in('paused','dormant'):l['tier']={'A':'B','B':'C'}[old]
    elif st=='unchecked' and a is None and A:pass
    if home=='Instagram is their website' and st=='active' and old=='B':l['tier']='A'
    c[(old,l['tier'],st)]+=1
json.dump(L,open(S+'leads/leads3.json','w'),separators=(',',':'))
t=collections.Counter(l['tier'] for l in L);print(t);print(collections.Counter(l.get('alive') for l in L if 'alive' in l));print(collections.Counter(l.get('home') for l in L if 'home' in l))
