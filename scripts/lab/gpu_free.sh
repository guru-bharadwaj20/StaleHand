#!/usr/bin/env bash
# Wait until GPU 0 has at least MIN_MB of free memory (other people's jobs share these cards).
# usage: gpu_free.sh MIN_MB [POLL_SECONDS]
set -euo pipefail
min="${1:?usage: gpu_free.sh MIN_MB [POLL_SECONDS]}" poll="${2:-60}"
while true; do
  free="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)"
  if [ "$free" -ge "$min" ]; then
    echo "GPU 0 has ${free} MiB free"
    exit 0
  fi
  sleep "$poll"
done
