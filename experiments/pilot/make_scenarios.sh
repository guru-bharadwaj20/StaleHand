#!/usr/bin/env bash
# Regenerate the pilot replication scenarios. Deterministic: the same seed gives byte-identical files.
# Each domain is also split into shards of 10 lines, so the runner can spread one domain over many parallel jobs.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m stalehand scenarios --domain inbox --n 10 --seed 0 --out inbox.jsonl
python3 -m stalehand scenarios --domain shop --n 5 --seed 0 --out shop.jsonl
rm -rf shards && mkdir shards
for d in inbox shop; do
  split -l 10 -d -a 2 --additional-suffix .jsonl "$d.jsonl" "shards/$d-"
done
