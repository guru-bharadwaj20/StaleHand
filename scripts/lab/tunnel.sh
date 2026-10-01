#!/usr/bin/env bash
# Make this box's model server reachable on another box's localhost through ssh, so no port is opened on the
# network. Run it on the box that serves the model; it needs passwordless ssh to the other box.
# usage: tunnel.sh PORT SSH_TARGET        (the server stays on 127.0.0.1:PORT here, and appears there on the same port)
set -euo pipefail
source "$(dirname "$0")/common.sh"
[ $# -eq 2 ] || { echo "usage: $0 PORT SSH_TARGET" >&2; exit 2; }
port="$1" target="$2"
mkdir -p "$STATE_DIR"
pidfile="$STATE_DIR/tunnel-$port.pid" log="$STATE_DIR/tunnel-$port.log"
if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2> /dev/null; then
  echo "already running: tunnel for :$port (pid $(cat "$pidfile"))"
  exit 0
fi
cmd=(ssh -N -o BatchMode=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4
     -R "127.0.0.1:$port:127.0.0.1:$port" "$target")
if [ -n "${DRY_RUN:-}" ]; then
  echo "${cmd[@]}"
  exit 0
fi
setsid nohup "${cmd[@]}" > "$log" 2>&1 < /dev/null &
echo $! > "$pidfile"
echo "tunnel :$port -> $target:$port (pid $!, log $log)"
