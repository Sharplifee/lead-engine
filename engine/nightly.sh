#!/bin/bash
# Nightly on the cloud computer: Gemini-judge any screenshots not yet judged by Gemini (stops when the free daily quota is used),
# then rescore everything and push the results to Supabase (table lead_engine_leads + Storage bucket lead-engine).
cd "$(dirname "$(dirname "$(readlink -f "$0")")")"
export LE_HOME="$PWD"; set -a; [ -f .env ] && . ./.env; set +a
mkdir -p logs
{
  echo "=== $(date -Is) nightly start"
  python3 engine/keys.py
  python3 engine/judge_gem.py
  bash engine/rebuild.sh
  python3 engine/sync.py push
  echo "=== $(date -Is) nightly done"
} >> logs/nightly.log 2>&1
