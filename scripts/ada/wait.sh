#!/usr/bin/env bash
# Block until the server on PORT lists its model, or fail after TIMEOUT seconds (default 900).
# usage: wait.sh PORT
set -euo pipefail
port="${1:?usage: wait.sh PORT}" timeout="${TIMEOUT:-900}"
for ((t = 0; t < timeout; t += 5)); do
  if curl -sf "http://127.0.0.1:$port/v1/models" > /dev/null; then
    echo "port $port ready after ${t}s"
    exit 0
  fi
  sleep 5
done
echo "port $port not ready after ${timeout}s" >&2
exit 1
