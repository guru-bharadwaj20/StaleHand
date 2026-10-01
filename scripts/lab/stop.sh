#!/usr/bin/env bash
# Stop the servers and tunnels that serve.sh and tunnel.sh started on this box, and nothing else.
set -euo pipefail
source "$(dirname "$0")/common.sh"
shopt -s nullglob
for pidfile in "$STATE_DIR"/*.pid; do
  if kill "$(cat "$pidfile")" 2> /dev/null; then echo "stopped $(basename "$pidfile" .pid)"; fi
  rm -f "$pidfile"
done
