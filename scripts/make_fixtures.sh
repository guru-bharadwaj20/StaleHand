#!/usr/bin/env bash
# Regenerate the shared scenario fixtures that the TypeScript, Go and Rust tests read.
set -euo pipefail
cd "$(dirname "$0")/.."
out=schema/fixtures
mkdir -p "$out"
stalehand scenarios --domain inbox --n 2 --seed 0 --out "$out/inbox.jsonl"
stalehand scenarios --domain shop --n 2 --seed 0 --out "$out/shop.jsonl"
stalehand scenarios --domain files --n 2 --seed 0 --out "$out/files.jsonl"
stalehand scenarios --domain tickets --n 2 --seed 0 --out "$out/tickets.jsonl"
stalehand scenarios --domain calendar --n 2 --seed 0 --out "$out/calendar.jsonl"
