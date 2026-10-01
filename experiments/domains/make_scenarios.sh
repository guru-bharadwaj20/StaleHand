#!/usr/bin/env bash
# Guard comparison on the four newer domains (files, tickets, calendar, chat), with the main comparison's setting:
# every change at step 0, landing after the handoff. Five first screens per task kind, in shards of 10.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf shards && mkdir shards
for d in files tickets calendar chat; do
  python3 -m stalehand scenarios --domain $d --n 5 --seed 0 --change-step 0 --out $d.jsonl
  split -l 10 -d -a 2 --additional-suffix .jsonl "$d.jsonl" "shards/$d-"
done
