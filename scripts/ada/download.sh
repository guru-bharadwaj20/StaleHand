#!/usr/bin/env bash
# Download model weights ahead of serving and record the exact revision of each.
# usage: download.sh NAME [NAME...]   (short names from src/stalehand/models/registry.py)
set -euo pipefail
source "$(dirname "$0")/common.sh"
[ $# -ge 1 ] || { echo "usage: $0 NAME [NAME...]" >&2; exit 2; }
mkdir -p "$STATE_DIR"
for name in "$@"; do
  id="$(hf_id "$name")"
  path="$("$SERVE_VENV/bin/hf" download "$id" --quiet)"
  # the snapshot directory is named after the commit, which run provenance needs
  echo "$name $id $(basename "$path")" | tee -a "$STATE_DIR/revisions.txt"
done
