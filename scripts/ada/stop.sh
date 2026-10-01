#!/usr/bin/env bash
# Stop every server started by serve.sh.
set -euo pipefail
source "$(dirname "$0")/common.sh"
shopt -s nullglob
for pidfile in "$STATE_DIR"/*.pid; do
  if kill "$(cat "$pidfile")" 2> /dev/null; then echo "stopped $(basename "$pidfile" .pid)"; fi
  rm -f "$pidfile"
done
