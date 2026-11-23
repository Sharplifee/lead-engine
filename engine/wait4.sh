T=$(cat /tmp/claude-0/-home-claude/3b82457b-0683-52d0-920c-2ae0e311ce4f/scratchpad/leads/.tok)
for r in "$@"; do until s=$(curl -s -H "Authorization: Bearer $T" https://api.apify.com/v2/actor-runs/$r | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['status'])"); [ "$s" != RUNNING ] && [ "$s" != READY ]; do sleep 20; done; echo "$r $s"; done
