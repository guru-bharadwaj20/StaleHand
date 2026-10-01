#!/usr/bin/env bash
# Main guard comparison scenarios: the pilot's tasks, with every change scheduled at step 0. Under the
# after_handoff timing it lands after the planner writes the first subtask and before the executor looks.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m stalehand scenarios --domain inbox --n 10 --seed 0 --change-step 0 --out inbox.jsonl
python3 -m stalehand scenarios --domain shop --n 5 --seed 0 --change-step 0 --out shop.jsonl
rm -rf shards && mkdir shards
for d in inbox shop; do
  split -l 10 -d -a 2 --additional-suffix .jsonl "$d.jsonl" "shards/$d-"
done
