# Lead Engine

Finds, verifies and ranks Utah County local businesses for the finished-site offer: rebuild a business's website unasked and offer the finished site.

## Where everything lives
- **Code:** this repo (`Sharplifee/lead-engine`). Installed on the cloud computer at `/srv/projects/lead-engine`.
- **Leads:** Supabase Corpus HQ (`lbvaosyfikkpvcwksiph`), table `public.lead_engine_leads`, one row per business with tier, score, layers, presence, activity and vision verdict.
- **Screenshots and working data:** Supabase Storage bucket `lead-engine` (`mshots/` phone screenshots, `leads/`, `social/`, `grok_in/` working files).
- **Keys:** never in this repo. `engine/keys.py` pulls them from `credentials_registry` (Apify row 26, Gemini rows 478 and 479) using `LE_SB_SECRET` from `.env`.

## Setup on any machine
```bash
git clone https://github.com/Sharplifee/lead-engine && cd lead-engine
echo "LE_SB_SECRET=<Corpus HQ sb_secret, credentials_registry row 471>" > .env
pip install pillow playwright && python3 -m playwright install chromium
python3 engine/keys.py      # writes leads/.tok, leads/.gem1, leads/.gem2
python3 engine/sync.py pull # downloads working data and screenshots
bash engine/rebuild.sh      # rescore everything and rebuild site/index.html
python3 engine/sync.py push # upserts lead_engine_leads and uploads new files
```

## Pipeline
| Step | Script | What it does |
|---|---|---|
| Verify sites | `audit.py`, `paths.py` | load every website, find booking/ordering/shop providers |
| Phone screenshots | `shot_m.py`, `reshoot_m.py`, `grok_shot.py` | iPhone-size capture of the first two screens plus phone metrics |
| Vision judge | `judge_gem.py` | Gemini (`gemini-flash-lite-latest`, falls back to `gemini-flash-latest`) rates each screenshot redesign / maybe / skip. Never OpenAI. Never Gemini key 445. |
| Score | `score2.py` (uses `score.py` helpers), `profiles.py` | six layers out of 100 and tiers A/B/C |
| Presence | `social1.py`, `social2.py`, `igparse.py`, `fbparse.py` | business Facebook/Instagram/TikTok pages only, never owners' personal profiles |
| Still open | `activity.py`, `layer3.py` | Google review recency, closed flags, hours; adjusts tiers |
| Bot sweep | `grok1.py`, `grok2.py`, `grok_merge_repeats.py`, `bot8_merge.py` | merge Grok research-bot CSVs (`grok_in/`), apply verifier fixes, dedupe, score |
| Page | `build_page3.py` | builds `site/index.html` plus screenshot sprite sheets for the Lead Engine artifact |
