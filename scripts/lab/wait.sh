#!/usr/bin/env bash
# Block until the server on HOST:PORT lists a model, or fail after TIMEOUT seconds (default 900).
# usage: wait.sh PORT [HOST]
set -euo pipefail
port="${1:?usage: wait.sh PORT [HOST]}" host="${2:-127.0.0.1}" timeout="${TIMEOUT:-900}"
for ((t = 0; t < timeout; t += 5)); do
  if curl -sf "http://$host:$port/v1/models" > /dev/null; then
    echo "$host:$port ready after ${t}s"
    exit 0
  fi
  sleep 5
done
echo "$host:$port not ready after ${timeout}s" >&2
exit 1
