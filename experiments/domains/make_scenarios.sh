#!/usr/bin/env bash
# Guard comparison scenarios for the files, tickets, calendar and chat domains, set up like experiments/main:
# every change at step 0, so under after_handoff it lands between the first subtask and the executor's look.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf shards && mkdir shards
for d in files tickets calendar chat; do
  python3 -m stalehand scenarios --domain "$d" --n 5 --seed 0 --change-step 0 --out "$d.jsonl"
  split -l 10 -d -a 2 --additional-suffix .jsonl "$d.jsonl" "shards/$d-"
done
