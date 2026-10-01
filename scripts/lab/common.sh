#!/usr/bin/env bash
# Shared settings for the lab 4090 boxes. Override any of them in the environment.
# The boxes are a shared account: these scripts only ever stop processes whose pid they wrote themselves.
STALEHAND_DIR="${STALEHAND_DIR:-$HOME/stalehand}"
STATE_DIR="${STATE_DIR:-$HOME/.stalehand/lab}"
PYTHON="${PYTHON:-python3}"
# transformers and torch come from $PYTHON; stalehand and playwright from these directories
export PYTHONPATH="$STALEHAND_DIR/src${EXTRA_PYTHONPATH:+:$EXTRA_PYTHONPATH}"
export HF_HOME="${HF_HOME:-$HOME/capstone_pilots/hf}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
# fewer out-of-memory failures from fragmentation on cards other jobs share
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
