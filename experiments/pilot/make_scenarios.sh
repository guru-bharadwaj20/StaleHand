#!/usr/bin/env bash
# Regenerate the pilot replication scenarios. Deterministic: the same seed gives byte-identical files.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m stalehand scenarios --domain inbox --n 10 --seed 0 --out inbox.jsonl
python3 -m stalehand scenarios --domain shop --n 5 --seed 0 --out shop.jsonl
