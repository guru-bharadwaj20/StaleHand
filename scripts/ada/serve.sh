#!/usr/bin/env bash
# Start one OpenAI-compatible vLLM server in the background.
# usage: serve.sh NAME PORT [GPU_FRACTION]
# The served model name is the hf id, which is what OpenAICompatVLM sends. Logs and pid go to $STATE_DIR.
set -euo pipefail
source "$(dirname "$0")/common.sh"
[ $# -ge 2 ] || { echo "usage: $0 NAME PORT [GPU_FRACTION]" >&2; exit 2; }
name="$1" port="$2" frac="${3:-0.9}"
id="$(hf_id "$name")"
args=(serve "$id" --served-model-name "$id" --host 127.0.0.1 --port "$port"
      --gpu-memory-utilization "$frac" --max-model-len "$MAX_MODEL_LEN" --seed 0
      --limit-mm-per-prompt '{"image": 1}')
[ "$QUANT" = none ] || args+=(--quantization "$QUANT")
# InternVL ships its config and image processor as remote code
case "$id" in OpenGVLab/*) args+=(--trust-remote-code) ;; esac
if [ -n "${DRY_RUN:-}" ]; then
  echo vllm "${args[@]}"
  exit 0
fi
mkdir -p "$STATE_DIR"
nohup "$SERVE_VENV/bin/vllm" "${args[@]}" > "$STATE_DIR/$name-$port.log" 2>&1 &
echo $! > "$STATE_DIR/$name-$port.pid"
echo "started $id on :$port (pid $!, log $STATE_DIR/$name-$port.log)"
