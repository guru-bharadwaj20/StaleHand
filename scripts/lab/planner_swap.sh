#!/usr/bin/env bash
# On the planner box: wait until the agent box has finished a matrix, then replace our planner with another model and
# tunnel it back. For campaigns where the agent box cannot ssh here (campaign.sh then waits for the new model on :8001).
# usage: planner_swap.sh AGENT_SSH DONE_FILE MODEL     e.g. planner_swap.sh ccbd@10.10.3.83 runs/domains.done qwen3-vl-4b
# Uses PYTHON, EXTRA_PYTHONPATH and MAX_BATCH like serve.sh. Stops only what serve.sh and tunnel.sh started here.
set -uo pipefail
source "$(dirname "$0")/common.sh"
[ $# -eq 3 ] || { sed -n 2,5p "$0" >&2; exit 2; }
agent="$1" done_file="$2" model="$3"
cd "$STALEHAND_DIR"
log() { echo "$(date "+%F %H:%M:%S") $*"; }
log "waiting for $done_file on $agent"
until ssh -o BatchMode=yes -o ConnectTimeout=15 "$agent" "test -f ~/stalehand/$done_file"; do sleep 30; done
log "$done_file is there; swapping the planner to $model"
scripts/lab/stop.sh
sleep 10
MAX_BATCH="${MAX_BATCH:-16}" scripts/lab/serve.sh "$model" 8001
TIMEOUT=1800 scripts/lab/wait.sh 8001 || { log "$model did not come up"; exit 1; }
scripts/lab/tunnel.sh 8001 "$agent"
log "planner $model serving and tunnelled to $agent"
