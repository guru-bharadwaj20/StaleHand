#!/usr/bin/env bash
# Serve a planner on :8000 and an executor on :8001 side by side, then wait for both.
# usage: pair.sh PLANNER EXECUTOR    e.g. pair.sh qwen3-vl-8b internvl3.5-8b
set -euo pipefail
dir="$(dirname "$0")"
[ $# -eq 2 ] || { echo "usage: $0 PLANNER EXECUTOR" >&2; exit 2; }
"$dir/serve.sh" "$1" 8000 0.45
"$dir/wait.sh" 8000   # start one at a time: two cold starts at once can both overcommit memory
"$dir/serve.sh" "$2" 8001 0.45
"$dir/wait.sh" 8001
