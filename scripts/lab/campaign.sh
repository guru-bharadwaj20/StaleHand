#!/usr/bin/env bash
# Run matrices back to back on the agent box, swapping the executor (this box) and the planner (PLANNER_SSH) only
# when the next matrix needs a different model. Run it on the agent box from ~/stalehand.
# usage: campaign.sh PLANNER_SSH ENTRY...
#   ENTRY = name:matrix:executor:planner   e.g. domains:experiments/domains/matrix.json:ui-tars-1.5-7b:qwen3-vl-8b
#   planner "none" runs an executor-only matrix.
# Settings: MAX_BATCH (default 16; the server halves it on out-of-memory), HOSTS (default runner/hosts.json),
#   PLANNER_PYTHON and PLANNER_EXTRA (PYTHON and EXTRA_PYTHONPATH on the planner box), RESETS (default 2: how many
#   times failed jobs are reset and rerun after the servers answer again).
# Like the other lab scripts it only stops servers whose pid files our own scripts wrote.
set -uo pipefail
source "$(dirname "$0")/common.sh"
[ $# -ge 2 ] || { sed -n 2,10p "$0" >&2; exit 2; }
planner_ssh="$1"; shift
cd "$STALEHAND_DIR"
hosts="${HOSTS:-runner/hosts.json}"
stalerun="${STALERUN:-$HOME/stalehand_bin/stalerun}"
log() { echo "$(date "+%F %H:%M:%S") $*"; }

running_model() {   # model served on PORT by our serve.sh, from its pid file, if that process is alive
  local port="$1" f
  for f in "$STATE_DIR"/*-"$port".pid; do
    [ -f "$f" ] && kill -0 "$(cat "$f")" 2> /dev/null && { basename "$f" "-$port.pid"; return; }
  done
}

ensure_executor() {
  local want="$1" have
  have="$(running_model 8002)"
  if [ "$have" != "$want" ]; then
    if [ -n "$have" ]; then
      log "stopping our executor $have"
      kill "$(cat "$STATE_DIR/$have-8002.pid")"; rm -f "$STATE_DIR/$have-8002.pid"; sleep 15
    fi
    MAX_BATCH="${MAX_BATCH:-16}" scripts/lab/serve.sh "$want" 8002
  fi
  TIMEOUT=1800 scripts/lab/wait.sh 8002
}

ensure_planner() {   # our planner server on the planner box, plus the tunnel that shows it here on :8001
  local want="$1"
  [ "$want" = none ] && return 0
  # shellcheck disable=SC2029
  ssh -o BatchMode=yes "$planner_ssh" "cd ~/stalehand && export PYTHON='${PLANNER_PYTHON:-python3}' \
    EXTRA_PYTHONPATH='${PLANNER_EXTRA:-}' MAX_BATCH='${MAX_BATCH:-16}' && \
    have=\$(for f in ~/.stalehand/lab/*-8001.pid; do [ -f \"\$f\" ] && kill -0 \"\$(cat \"\$f\")\" 2>/dev/null && basename \"\$f\" -8001.pid; done) && \
    if [ \"\$have\" != '$want' ]; then scripts/lab/stop.sh; scripts/lab/serve.sh '$want' 8001; fi && \
    TIMEOUT=1800 scripts/lab/wait.sh 8001 && scripts/lab/tunnel.sh 8001 '${AGENT_SSH:?set AGENT_SSH to user@this-box}'" \
    || return 1
  TIMEOUT=600 scripts/lab/wait.sh 8001
}

failed_count() {
  python3 -c "import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute(\"select count(*) from jobs where status='failed'\").fetchone()[0])" "$1"
}

reset_failed() {   # failed jobs go back to pending with their attempts cleared
  python3 - "$1" << 'EOF'
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
n = c.execute("UPDATE jobs SET status = 'pending', attempts = 0 WHERE status = 'failed'").rowcount
c.commit()
print(f"reset {n} failed jobs")
EOF
}

host_name="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["hosts"][0]["name"])' "$hosts")"
for entry in "$@"; do
  IFS=: read -r name matrix executor planner <<< "$entry"
  if [ -f "runs/$name.done" ]; then log "skip $name (done)"; continue; fi
  log "== $name: executor $executor, planner $planner"
  ensure_executor "$executor" || { log "executor $executor did not come up"; exit 1; }
  ensure_planner "$planner" || { log "planner $planner did not come up"; exit 1; }
  db="runs/$name.db"
  "$stalerun" plan -matrix "$matrix" -db "$db"
  "$stalerun" release -db "$db" -host "$host_name" || true   # jobs left running by an interrupted campaign
  for round in $(seq 0 "${RESETS:-2}"); do
    "$stalerun" run -db "$db" -hosts "$hosts" -logs "runs/logs/$name"
    "$stalerun" status -db "$db"
    failed="$(failed_count "$db")"
    [ "$failed" = 0 ] || [ "$round" = "${RESETS:-2}" ] && break
    log "$failed failed jobs; rerun $((round + 1)) once the servers answer"
    TIMEOUT=1800 scripts/lab/wait.sh 8002 || exit 1
    [ "$planner" = none ] || TIMEOUT=1800 scripts/lab/wait.sh 8001 || exit 1
    reset_failed "$db"
  done
  touch "runs/$name.done"
  log "== $name finished"
done
log "campaign finished"
