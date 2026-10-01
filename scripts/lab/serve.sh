#!/usr/bin/env bash
# Start `stalehand serve` for one model in the background, detached from the ssh session.
# usage: serve.sh NAME PORT        (NAME is a short name from stalehand.models.registry; MAX_BATCH, default 8)
set -euo pipefail
source "$(dirname "$0")/common.sh"
[ $# -eq 2 ] || { echo "usage: $0 NAME PORT" >&2; exit 2; }
name="$1" port="$2"
mkdir -p "$STATE_DIR"
pidfile="$STATE_DIR/$name-$port.pid" log="$STATE_DIR/$name-$port.log"
if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2> /dev/null; then
  echo "already running: $name on :$port (pid $(cat "$pidfile"))"
  exit 0
fi
cmd=("$PYTHON" -m stalehand serve --model "$name" --port "$port" --max-batch "${MAX_BATCH:-8}")
if [ -n "${DRY_RUN:-}" ]; then
  echo "${cmd[@]}"
  exit 0
fi
setsid nohup "${cmd[@]}" > "$log" 2>&1 < /dev/null &
echo $! > "$pidfile"
echo "started $name on :$port (pid $!, log $log)"
