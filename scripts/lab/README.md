# Lab serving

The lab boxes each have one 24 GB RTX 4090, and other people's jobs share them. The planner (Qwen3-VL-8B) and the
executor (UI-TARS-1.5-7B) need about 17 GB each in bf16, so each box serves one model:

| Box | Serves | Runs |
|---|---|---|
| agent box | executor on `127.0.0.1:8002` | Chrome, `stalerun`, `stalehand run-job` |
| planner box | planner on `127.0.0.1:8001` | `tunnel.sh`, which makes port 8001 appear on the agent box |

Both servers listen only on localhost. The planner box reaches the agent box over ssh (`tunnel.sh` opens a reverse
forward), so nothing is opened on the network.

## Start

On the planner box:

```bash
scripts/lab/gpu_free.sh 20000              # wait until other jobs leave room
scripts/lab/serve.sh qwen3-vl-8b 8001
scripts/lab/wait.sh 8001
scripts/lab/tunnel.sh 8001 user@agent-box
```

On the agent box:

```bash
scripts/lab/gpu_free.sh 20000
scripts/lab/serve.sh ui-tars-1.5-7b 8002
scripts/lab/wait.sh 8002 && scripts/lab/wait.sh 8001
```

The agent box's entry in `runner/hosts.json` then points `run-job` at both ports:

```json
{"name": "agent", "slots": 2, "workdir": "~/stalehand", "python": "python3",
 "env": {"STALEHAND_BACKEND": "openai", "STALEHAND_PLANNER_URL": "http://127.0.0.1:8001/v1",
         "STALEHAND_EXECUTOR_URL": "http://127.0.0.1:8002/v1", "PYTHONPATH": "src:../stalehand_lib"}}
```

## Settings

`common.sh` reads `PYTHON` (the interpreter with torch and transformers), `EXTRA_PYTHONPATH` (where Playwright,
Pillow or a matching torchvision were installed with `pip install --target`), `HF_HOME` and `STALEHAND_DIR`.
Weights load offline from `HF_HOME`.

## Stop

`scripts/lab/stop.sh` stops the servers and tunnels that these scripts started on this box. It reads their pid
files and never matches processes by name.
