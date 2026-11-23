"""Write the API keys the engine needs into leads/ dotfiles, pulled from Corpus HQ credentials_registry.
Needs LE_SB_SECRET (Corpus HQ sb_secret, registry row 471) in the environment or in LE_HOME/.env.
Rows: 26 Apify token -> leads/.tok, 478 Gemini (vision judge) -> leads/.gem1, 479 Gemini fallback -> leads/.gem2.
Never OpenAI, never Gemini key 445 (Skipper's)."""
import os,json,urllib.request
LE_HOME=os.environ.get('LE_HOME',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def secret():
    s=os.environ.get('LE_SB_SECRET')
    if not s and os.path.exists(LE_HOME+'/.env'):
        for line in open(LE_HOME+'/.env'):
            if line.startswith('LE_SB_SECRET='):s=line.split('=',1)[1].strip()
    if not s:raise SystemExit('Set LE_SB_SECRET (Corpus HQ sb_secret, credentials_registry row 471)')
    return s
SB='https://lbvaosyfikkpvcwksiph.supabase.co'
if __name__=='__main__':
    k=secret()
    rows=json.load(urllib.request.urlopen(urllib.request.Request(SB+'/rest/v1/credentials_registry?id=in.(26,478,479)&select=id,value',headers={'apikey':k,'Authorization':'Bearer '+k})))
    m={26:'.tok',478:'.gem1',479:'.gem2'};os.makedirs(LE_HOME+'/leads',exist_ok=True)
    for r in rows:
        p=LE_HOME+'/leads/'+m[r['id']]
        with open(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600),'w') as f:f.write(r['value'].strip())
    print('wrote',sorted(m[r['id']] for r in rows))
