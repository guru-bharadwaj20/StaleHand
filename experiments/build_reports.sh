#!/usr/bin/env bash
# Rebuild every report under results/vivian-4090/ (markdown and SVG charts) and the README results section.
# Every number in them is read from results.jsonl files; nothing is typed in by hand.
set -euo pipefail
cd "$(dirname "$0")/.."
for dir in results/vivian-4090/*/; do
  name=$(basename "$dir")
  if find "$dir" -name results.jsonl -print -quit | grep -q .; then
    python3 -m stalehand report --runs "$dir" --out "results/vivian-4090/${name}_report.md" --charts
  fi
done
python3 experiments/audit/summarize.py results/vivian-4090 > results/vivian-4090/checks_report.md
python3 -m stalehand readme
