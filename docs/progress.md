# Progress

Runs that failed, were skipped or are blocked are recorded here rather than dropped (see `CONTRIBUTING.md`).

## Blocked

- **Second-family experiments (`results/guru-4500/`)**, 2026-10-01. Not run: the main matrices they rerun do not
  exist yet, and `stalehand run-job` (the entry point the runner calls) is still open. Ready on Guru's side:
  `internvl3.5-8b` in the model registry and `scripts/ada/` to serve it next to the planner. Unblocks once
  `run-job` lands and the main inbox and shop comparison has a config to rerun.
  Checked on the Ada on 2026-10-01: `scripts/ada/setup.sh` installs vLLM 0.30.0 with CUDA available, and
  `scripts/ada/download.sh` fetched Qwen/Qwen3-VL-8B-Instruct at 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b and
  OpenGVLab/InternVL3_5-8B at 9bb6a56ad9cc69db95e2d4eeb15a52bbcac4ef79. Serving was not started: another
  project's vLLM server held 22.9 of 24.5 GB on the card and was left running.

## Discarded or partial runs

- **Pilot, first attempt**, 2026-10-01 16:36–16:39 on worker-1 and worker-2. The planner server on worker-2 died
  at 16:39, with no error in its log, at the same moment as another team's job on that card. All 42 jobs then used
  up their three attempts within seconds. 5 episodes had finished. Fixed in `openai_compat.py`: model calls now
  retry for up to 15 minutes while a server or tunnel is down.
- **Pilot, second attempt** (`runs/pilot_invalid_v1` on worker-1, 116 episodes), discarded. Two problems made those
  episodes unusable:
  - The shop showed a Filters and Sort sidebar that did nothing, and the agent clicked it until it ran out of steps.
  - `replan_every_step` erased the executor's action history even when the planner handed back the same subtask.
  Both are fixed (`fix: remove dead shop filter controls`, `fix: keep history on unchanged replans`).
- **Pilot, shop tasks on a relative criterion** (`results/vivian-4090/pilot`, shop cheapest and highest rated rows).
  Kept, but they don't measure staleness. The results bar still read "sorted by relevance", the planner kept
  asking to sort, and the executor searched for a sort control that does not exist. Rerun as `pilot_shop_rerun`
  after `fix: drop sort wording from shop results`. Use those rows for shop relative tasks instead.
