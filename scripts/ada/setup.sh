#!/usr/bin/env bash
# Create the serving virtualenv with a pinned vLLM. Run once per workstation.
set -euo pipefail
source "$(dirname "$0")/common.sh"
python3 -m venv "$SERVE_VENV"
"$SERVE_VENV/bin/pip" install --upgrade pip
"$SERVE_VENV/bin/pip" install "vllm==$VLLM_VERSION"
"$SERVE_VENV/bin/python" -c 'import torch, vllm; print("vllm", vllm.__version__, "torch", torch.__version__, "cuda", torch.cuda.is_available())'
