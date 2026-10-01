# Progress

Runs that failed, were skipped or are blocked are recorded here rather than dropped (see `CONTRIBUTING.md`).

## Blocked

- **Second-family experiments and new-domain guard comparison (`results/guru-4500/`)**, 2026-10-01. Not run.
  The configs are ready: `experiments/second_family/matrix.json` and `matrix_timing.json` (the main and timing
  matrices with `internvl3.5-8b` as executor) and `experiments/domains/` (60 scenarios each for files, tickets,
  calendar and chat, change at step 0, the main matrix's eight guards, UI-TARS executor). `stalerun` now builds
  on Windows, so jobs can run on the Ada next to Chrome. What blocks them is memory: in fp8 with an 8192-token
  context, vLLM 0.30.0 could not fit Qwen3-VL-8B in 0.45, 0.48 or 0.5 of the card ("Available KV cache memory:
  -1.04 GiB" at 0.48, after 9.9 GiB of weights), so a planner and an executor cannot share the 24 GB card as
  `scripts/ada/pair.sh` assumes. Options: serve the planner from another machine (a lab 4090 through
  `scripts/lab/tunnel.sh`), or use a smaller planner, which would change the comparison with the main results.
  Port 8000 on the Ada was also held by another project's vLLM server; it was left running.

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
