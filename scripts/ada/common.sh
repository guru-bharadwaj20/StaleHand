# shellcheck shell=bash
# Shared settings for the RTX 4500 Ada serving scripts. Override any of these in the environment.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVE_VENV="${SERVE_VENV:-$HOME/stalehand-serve}"
VLLM_VERSION="${VLLM_VERSION:-0.30.0}"
STATE_DIR="${STATE_DIR:-$REPO/runs/ada}"
# 24 GB holds one 8B model in bf16, or a planner and an executor side by side in fp8 (Ada supports fp8).
QUANT="${QUANT:-fp8}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"

# hf id for a short model name, read from the model registry so the two never disagree
hf_id() {
  PYTHONPATH="$REPO/src" python3 -c 'import sys
from stalehand.models.registry import MODELS
print(MODELS[sys.argv[1]].hf_id)' "$1"
}
