#!/bin/bash
# Full rebuild in order: base presence/alive layers, bot-sweep wave, bot repeats, Bot 8 enrichment, page.
set -e
cd "${LE_HOME:-$(dirname "$(dirname "$(readlink -f "$0")")")}"
export LE_HOME="$PWD"
set -a; [ -f .env ] && . ./.env; set +a
python3 engine/score2.py
python3 engine/layer3.py
python3 engine/grok1.py
python3 engine/grok2.py
python3 engine/grok_merge_repeats.py
python3 engine/bot8_merge.py
python3 engine/build_page3.py
