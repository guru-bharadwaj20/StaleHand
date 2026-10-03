# Contributing

Two people work on this repository: Vivian and Guru. This file holds the plan, the task split and the working
rules. ✅ means done and merged; ❌ means still to do.

## Progress at a glance

| Phase | Name | Roadmap milestones | Commit budget | Done | Left | Status |
|---|---|---|---|---|---|---|
| 1 | Shared schemas | M0 | 15 | 2 | 0 | ✅ |
| 2 | Scenario core | M1 | 45 | 2 | 0 | ✅ |
| 3 | Web apps and environment | M2, M3 | 90 | 5 | 0 | ✅ |
| 4 | Models and agents | M4, M5 | 85 | 8 | 0 | ✅ |
| 5 | Guards | M6 | 55 | 4 | 0 | ✅ |
| 6 | Metrics and statistics | M7 | 40 | 4 | 0 | ✅ |
| 7 | Runner | M8 | 45 | 3 | 0 | ✅ |
| 8 | More domains | M9 | 50 | 4 | 0 | ✅ |
| 9 | Experiments | M10 | 40 | 17 | 0 | ✅ |
| 10 | Reports, docs and release | M11 | 30 | 11 | 0 | ✅ |
| | **Total** | | **495** | **61** | **0** | **100% done** |

Remaining work: **none**.

Each phase ends with tests passing and a short note in `docs/progress.md`. Commit budgets are for planning;
every commit is one real change (see [Commits](#commits)).

## Phase 1: Shared schemas (M0)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Scenario, episode and result JSON Schemas | Vivian | `schema/` |
| ✅ | Shared fixtures checked from every language | Vivian | `schema/fixtures/` |

## Phase 2: Scenario core (M1)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Items, criteria, resolver, change events, relevance | Vivian | `src/stalehand/scenarios/` |
| ✅ | Inbox and shop generators, JSONL export, `stalehand scenarios` command | Vivian | `src/stalehand/scenarios/domains/`, `src/stalehand/cli.py` |

## Phase 3: Web apps and environment (M2, M3)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Inbox and shop web apps, page harness, bundler | Vivian | `apps/src/{core,inbox,shop}/`, `apps/build.mjs` |
| ✅ | Playwright environment: actions, change timing, DOM mutation tracking, event steps | Vivian | `src/stalehand/env/` |
| ✅ | Handoff change timing: the change lands after the planner writes a subtask and before the executor's next screenshot | Vivian | `src/stalehand/env/`, `src/stalehand/agents/` |
| ✅ | **Gate:** a scripted agent finishes forward-the-email in the live inbox, and a change at step 2 shows in the screenshot and DOM log | Vivian | `tests/env/` |
| ✅ | Static render mode (render a scenario state to a screenshot without a live episode): `stalehand render` | Vivian | `src/stalehand/env/browser.py`, `results/figures/` |

## Phase 4: Models and agents (M4, M5)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Model backends (scripted, OpenAI-compatible, transformers) and output parsers | Vivian | `src/stalehand/models/` |
| ✅ | Hierarchical planner-executor agent and trajectory log | Vivian | `src/stalehand/agents/` |
| ✅ | Delegated agent (orchestrator and GUI operator, CoAct-1 style) | Vivian | `src/stalehand/agents/delegated.py` |
| ✅ | Flat agent (one policy per step, Agent S3 style), as a reference | Vivian | `src/stalehand/agents/flat.py` |
| ✅ | Model serving scripts for the lab boxes | Vivian | `scripts/lab/` |
| ✅ | Model serving on the RTX 4500 Ada (vLLM, OpenAI-compatible endpoint) | Guru | `scripts/ada/` |
| ✅ | Second executor family (InternVL3.5) in the model registry | Guru | `src/stalehand/models/registry.py` |
| ✅ | **Gate:** pilot reproduces in the live environment (stale subtask well below fresh on relative tasks) | Vivian | `results/vivian-4090/` |

## Phase 5: Guards (M6)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Guards: none, re-plan every step, self-check, rule subtask, DOM change, pixel change | Vivian | `src/stalehand/guards/` |
| ✅ | Rebind guard: re-resolve the rule each step, re-plan only if the target moved | Vivian | `src/stalehand/guards/rebind.py` |
| ✅ | `screendiff` crate: pixel difference and SSIM | Vivian | `crates/screendiff/` |
| ✅ | Pixel guard threshold calibration at handoff, all six domains | Vivian | `experiments/calibration/`, `results/vivian-4090/calibration/` |

## Phase 6: Metrics and statistics (M7)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Episode outcome scoring | Vivian | `src/stalehand/metrics/outcome.py` |
| ✅ | Paired statistics: exact McNemar, cluster bootstrap over scenario templates | Vivian | `src/stalehand/metrics/stats.py` |
| ✅ | `stalestats` crate, checked against the Python statistics on the same files | Guru | `crates/stalestats/` |
| ✅ | Full cost accounting: model calls, model seconds and actions per episode in every guard report; output and image tokens recounted from trajectories (prompt text was not logged) | Vivian | `src/stalehand/report/build.py`, `experiments/analysis/tokens.py`, `results/vivian-4090/tokens_report.md` |

**Gate:** every number in a summary table can be traced to a JSONL row.

## Phase 7: Runner (M8)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Go runner: matrix, SQLite job store, ssh dispatch, resume, `stalerun` command | Vivian | `runner/` |
| ✅ | `stalehand run-job` command, the entry point the Go runner calls | Vivian | `src/stalehand/cli.py`, `src/stalehand/run/` |
| ✅ | Provenance (git commit, model revisions, library versions) and result collection | Vivian | `runner/`, `src/stalehand/run/` |

## Phase 8: More domains (M9)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Files domain ("share the newest report"; uploads, renames) | Guru | `.../domains/files.py`, `apps/src/files/` |
| ✅ | Tickets domain ("assign the oldest high-priority ticket"; new tickets, priority changes) | Guru | `.../domains/tickets.py`, `apps/src/tickets/` |
| ✅ | Calendar domain ("join the next meeting with Kenji"; reschedules, cancellations) | Guru | `.../domains/calendar.py`, `apps/src/calendar/` |
| ✅ | Chat domain ("reply to the latest message from Grace"; new and edited messages) | Guru | `.../domains/chat.py`, `apps/src/chat/` |

## Phase 9: Experiments (M10)

The lab 4090s run Vivian's matrices back to back overnight on 1–2 October, from a queue on worker-1
(`scripts/lab/README.md`). Guru's Ada is busy with other work, so from 2 October every GPU run is Vivian's
(agreed by both): the lab boxes also take the matrices in `experiments/small_planner/`, `experiments/second_family/` and
`experiments/domains/`, serving one model per box where a pair does not fit one card. Guru takes the CPU work.

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Pilot replication on inbox and shop | Vivian | `results/vivian-4090/pilot/` |
| ✅ | Shop relative-task rerun | Vivian | `results/vivian-4090/pilot_shop_rerun/` |
| ✅ | Main guard comparison matrix and scenarios | Vivian | `experiments/main/matrix.json` |
| ✅ | Change-timing study matrix | Vivian | `experiments/main/matrix_timing.json` |
| ✅ | Model-free checks on the 1080 box: oracle audit of all 790 scenarios, click hazard at mid-step, pixel change at handoff | Vivian | `experiments/audit/`, `experiments/calibration/`, `results/vivian-4090/checks_report.md` |
| ✅ | Run the main guard comparison on inbox and shop | Vivian | `results/vivian-4090/main/`, `main_report.md` |
| ✅ | Click-loop table: how many episodes end with the executor clicking one spot | Vivian | `results/vivian-4090/loops_report.md` |
| ✅ | Run the change-timing study | Vivian | `results/vivian-4090/timing/`, `timing_report.md`, `contrasts_report.md`, `recovery_report.md` |
| ✅ | Run the stall-return ablation: main scenarios, three guards, executor hands back after two actions that change nothing | Vivian | `experiments/main/matrix_stall.json`, `results/vivian-4090/main_stall/` |
| ✅ | Run the delegated architecture with four guards | Vivian | `results/vivian-4090/delegated/` |
| ✅ | Run the three-guard comparison on files, tickets, calendar and chat (partial; superseded by the eight-guard run) | Vivian | `results/vivian-4090/domains_lab/` |
| ✅ | Run the flat reference in bf16 | Vivian | `results/vivian-4090/flat/` |
| ✅ | Change-kind and task-kind breakdowns in every guard report | Vivian | `results/vivian-4090/*_report.md` |
| ✅ | InternVL3.5 flat run: the action-format gate (parse failures, success with no change) before any hierarchical second-family run | Vivian | `experiments/second_family/flat.json`, `results/vivian-4090/` |
| ✅ | Small-planner arm: Qwen3-VL-4B planner and UI-TARS executor, bf16, four guards | Vivian | `experiments/small_planner/matrix.json`, `results/vivian-4090/small_planner/` |
| ✅ | Second-family hierarchical runs: dropped, InternVL failed the action-format gate (`results/REPORT.md`) | Vivian | `experiments/second_family/` |
| ✅ | Eight-guard comparison on the four new domains (planner and executor on separate lab boxes) | Vivian | `experiments/domains/matrix.json`, `results/vivian-4090/domains/` |

## Phase 10: Reports, docs and release (M11)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Report builder that reads result files | Vivian | `src/stalehand/report/` |
| ✅ | Paired contrasts across run sets (architecture, change timing), Holm-adjusted | Vivian | `src/stalehand/report/contrasts.py` |
| ✅ | Results explorer: static site that reads and validates result JSONL | Guru | `site/` |
| ✅ | Load tonight's lab results (main, timing, delegated, flat, domains) into the explorer as they land (built in from `results/` on every build; later runs load on rebuild) | Guru | `site/` |
| ✅ | Combined final report across both machines' results | Guru | `src/stalehand/report/` |
| ✅ | Charts for the main results (guard vs. stale rate, false alarms, cost) | Guru | `site/` |
| ✅ | Results section in `README.md`, generated from result files | Guru | `README.md` |
| ✅ | Usage guide: generate scenarios, serve models, run a matrix, build a report | Guru | `docs/` |
| ✅ | Worked examples (one scenario end to end, adding a new domain) | Guru | `docs/`, `examples/` |
| ✅ | Choose a license before the repository is made public (MIT) | Guru | `LICENSE` |
| ✅ | Decide whether to add a real application (for example a self-hosted mail client) | Guru | `docs/design.md` |

## Who does what next

| # | Vivian | Guru |
|---|---|---|
| 1 | ✅ Run the change-timing study | ✅ Load tonight's results into the explorer |
| 2 | ✅ Run the stall-return ablation | ✅ Combined final report |
| 3 | ✅ Run the delegated architecture | ✅ Choose a license |
| 4 | ✅ Finish the three-guard comparison on the new domains (superseded by 9) | ✅ Check why files and tickets fail under every guard (floor effect; see `docs/progress.md`) |
| 5 | ✅ Run the flat reference in bf16 | |
| 6 | ✅ InternVL3.5 flat run and action-format gate (failed) | |
| 7 | ✅ Small-planner arm | |
| 8 | ✅ Second-family hierarchical runs (dropped after the gate) | |
| 9 | ✅ Eight-guard comparison on the new domains | |
| 10 | ✅ Change-kind and task-kind breakdowns | |
| 11 | ✅ Full cost accounting | |
| 12 | ✅ Static render mode | |

All GPU runs are Vivian's and all CPU work is Guru's, as agreed on 2 October because the Ada is busy. Guru's
tasks read result files only, so they follow the lab runs as they land.

## Hardware

| Person | Machines | Used for |
|---|---|---|
| Vivian | two lab RTX 4090 boxes (24 GB each), a lab box with 4x GTX 1080 (8 GB each, no bf16), laptop | every GPU run, including the second family and small-planner arm; the 1080s take models up to about 2B, quantized arms and CPU or browser work |
| Guru | RTX 4500 Ada workstation (24 GB; one 8B model in bf16, or a 4B planner and a 7B executor in fp8) | CPU work only (the card is busy): results site, final report, license |

Runs stay on their owner's machines and write to separate result directories (`results/vivian-4090/`,
`results/guru-4500/`), so no two runs ever write the same file.

## Keeping the two halves independent

- **Contracts.** The halves meet only at `schema/*.schema.json`, the `window.stalehand` page API
  (`apps/src/core/harness.ts`), the model interface (`src/stalehand/models/base.py`) and the guard interface
  (`src/stalehand/guards/base.py`). Changing a contract needs a pull request that both people approve.
- **No shared lists to edit.** New scenario domains are discovered from `scenarios/domains/`, and new apps from
  `apps/src/*/main.ts`, so adding a domain touches only new files.
- **Branches.** Guru works on `guru/<topic>` and merges to `main` through a pull request with CI green. Vivian
  commits straight to `main`, with the tests passing before every push. Never force-push `main`.
- **Authorship.** Each person commits under their own name and follows the commit rules below.
- **Cross-checks.** The Python statistics (Vivian) and the Rust statistics (Guru) must agree on the same result
  files; a test in each language reads a shared fixture under `schema/fixtures/`.

## Commits

- One logical change per commit. Tests pass at every commit.
- Subject line only, in the form `<type>: <description>`, with a 4 to 6 word description.
- Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `exp` (experiment results).
- No trailers.
- Commit as each piece lands; do not batch a day's work into one commit.

Good: `feat: add newest-first ordering to resolver`, `exp: add inbox pilot replication results`
Bad: `update code`, `fix stuff`, `wip`

## Tests

- Metrics, statistics and the resolver are written test first: they fail quietly and return plausible numbers.
- Unit tests must not need a GPU or a network. Use the scripted model backend.
- Browser tests are marked `browser` and use the system Chrome through Playwright.

## Results

- Never write a number into a doc or report by hand. Reports read result files.
- Every run directory holds `config.json` with the seed, model revisions and library versions.
- A failed or skipped run is recorded in `docs/progress.md`, not dropped.
