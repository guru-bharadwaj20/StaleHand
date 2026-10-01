# Using StaleHand

This guide goes from a fresh checkout to a report: generate scenarios, serve the models, run a matrix and
build the report. Commands run from the repository root.

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev,render,stats]"   # Windows: .venv\Scripts\pip
(cd apps && npm ci && npm run build)             # apps/dist/<domain>.html, one page per domain
.venv/bin/pytest -m "not browser"                # no GPU, network or browser needed
```

Browser tests (`pytest -m browser`) drive the built apps in the system Chrome.

## 1. Generate scenarios

A scenario is one first screen, one task and one change. `stalehand scenarios` writes them as JSONL:

```bash
python -m stalehand scenarios --domain inbox --n 10 --seed 0 --change-step 0 --out inbox.jsonl
```

| Flag | Meaning |
|---|---|
| `--domain` | `inbox`, `shop`, `files`, `tickets`, `calendar` or `chat` |
| `--n` | first screens per task kind; each screen gets every change variant |
| `--seed` | the same seed always gives the same file |
| `--kinds`, `--variants` | comma-separated subsets (default: all) |
| `--change-step` | the step the change lands on; 0 with the `after_handoff` timing puts it between the planner's first subtask and the executor's first look |

Experiments keep a `make_scenarios.sh` next to their matrix (see `experiments/main/`) and split the JSONL into
shards of 10, so a matrix job is small enough to rerun.

## 2. Serve the models

Every model runs behind an OpenAI-compatible server, and `run-job` reaches it over HTTP.

- RTX 4500 Ada (vLLM, planner and executor on one card in fp8): [`scripts/ada/README.md`](../scripts/ada/README.md).
- Lab RTX 4090 boxes (one model per box, ssh tunnel between them): [`scripts/lab/README.md`](../scripts/lab/README.md).
- No vLLM: `python -m stalehand serve --model qwen3-vl-8b --port 8000` serves one model with transformers.

Model short names (`qwen3-vl-8b`, `ui-tars-1.5-7b`, `internvl3.5-8b`, ...) come from
`src/stalehand/models/registry.py`. Unit tests never need a server; they use the scripted backend.

## 3. Run a matrix

A matrix (`experiments/*/matrix*.json`) lists scenario shards, architectures, guards, planners, executors,
seeds, change timings and a step budget. The Go runner expands it into one job per combination and keeps them
in a SQLite file, so a stopped run resumes where it left off.

```bash
(cd runner && go build -o stalerun ./cmd/stalerun)
runner/stalerun plan -db runs/main.db -matrix experiments/main/matrix.json
runner/stalerun run  -db runs/main.db -hosts runner/hosts.json -logs runs/logs
runner/stalerun status -db runs/main.db
runner/stalerun collect -db runs/main.db -hosts runner/hosts.json -dest results/<you>   # copies to results/<you>/<matrix>/<job id>/
```

`runner/hosts.json` (not committed; copy `runner/hosts.example.json`) says where jobs run and how they reach the
models. A host with no `ssh` runs jobs on this machine:

```json
{"hosts": [
  {"name": "ada", "slots": 3, "workdir": ".", "python": ".venv/bin/python",
   "env": {"STALEHAND_BACKEND": "openai",
           "STALEHAND_PLANNER_URL": "http://127.0.0.1:8000/v1",
           "STALEHAND_EXECUTOR_URL": "http://127.0.0.1:8001/v1"}}
]}
```

Each job writes `runs/<matrix>/<job id>/` with `config.json` (git commit, seed, model revisions, library
versions), `results.jsonl` (one scored row per episode, checked against `schema/result.schema.json`) and the
trajectories. To run one job by hand, pass its spec to `stalehand run-job --job <base64 JSON> --out <dir>`;
rerunning into the same directory resumes it.

Results go under your machine's directory (`results/vivian-4090/`, `results/guru-4500/`), never someone
else's. A failed or skipped run is written up in [`progress.md`](progress.md).

## 4. Build the report

```bash
python -m stalehand report --runs results/vivian-4090/main --out report.md
```

The report reads only `results.jsonl` files: outcome rates per guard, domain, task kind and change kind, false
alarms on harmless changes, and each guard paired against `--baseline` (default `none`) with a bootstrap
interval over scenario templates and an exact McNemar test.

To browse the same rows, build the results explorer (`cd site && npm ci && npm run build`) and open
`site/dist/index.html`; see [`site/README.md`](../site/README.md).
