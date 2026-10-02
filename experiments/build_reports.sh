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
# run sets on the main scenarios, paired across architecture and change timing
sets=()
for name in main timing delegated flat main_stall; do
  if [ -d "results/vivian-4090/$name" ]; then sets+=("results/vivian-4090/$name"); fi
done
if [ "${#sets[@]}" -gt 1 ]; then
  python3 -m stalehand contrasts --runs "${sets[@]}" --out results/vivian-4090/contrasts_report.md
fi
runs=()
for dir in results/vivian-4090/*/; do
  if [ -f "$(find "$dir" -name results.jsonl -print -quit)" ]; then runs+=("${dir%/}"); fi
done
python3 -m stalehand.report.loops "${runs[@]}" > results/vivian-4090/loops_report.md
python3 -m stalehand.report.recovery "${runs[@]}" > results/vivian-4090/recovery_report.md
if compgen -G "results/vivian-4090/tokens/*.jsonl" > /dev/null; then
  python3 experiments/analysis/tokens.py report results/vivian-4090/tokens/*.jsonl > results/vivian-4090/tokens_report.md
fi
python3 experiments/audit/summarize.py results/vivian-4090 > results/vivian-4090/checks_report.md
python3 -m stalehand readme
python3 -m stalehand final --results results/vivian-4090 --sets main timing main_stall delegated flat small_planner domains flat_internvl \
  --template docs/report_template.md --out results/REPORT.md
