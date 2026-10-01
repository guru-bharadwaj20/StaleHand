# Contributing

Two people work on this repository: Vivian and Guru. This file holds the plan, the task split and the working
rules. ✅ means done and merged; ❌ means still to do.

## Progress at a glance

| Phase | Name | Roadmap milestones | Commit budget | Done | Left | Status |
|---|---|---|---|---|---|---|
| 1 | Shared schemas | M0 | 15 | 2 | 0 | ✅ |
| 2 | Scenario core | M1 | 45 | 2 | 0 | ✅ |
| 3 | Web apps and environment | M2, M3 | 90 | 4 | 1 | ❌ |
| 4 | Models and agents | M4, M5 | 85 | 8 | 0 | ✅ |
| 5 | Guards | M6 | 55 | 4 | 0 | ✅ |
| 6 | Metrics and statistics | M7 | 40 | 3 | 1 | ❌ |
| 7 | Runner | M8 | 45 | 3 | 0 | ✅ |
| 8 | More domains | M9 | 50 | 4 | 0 | ✅ |
| 9 | Experiments | M10 | 40 | 4 | 5 | ❌ |
| 10 | Reports, docs and release | M11 | 30 | 2 | 7 | ❌ |
| | **Total** | | **495** | **36** | **14** | **72% done** |

Remaining work: **14 tasks**, split 7 to Vivian and 7 to Guru (see [Who does what next](#who-does-what-next)).

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
| ❌ | Static render mode (render a scenario state to a screenshot without a live episode) | Vivian | `src/stalehand/env/` |

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
| ❌ | Full cost accounting: tokens, wall-clock time and planner calls per episode, in the report tables | Vivian | `src/stalehand/metrics/`, `src/stalehand/report/` |

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

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Pilot replication on inbox and shop | Vivian | `results/vivian-4090/pilot/` |
| ✅ | Shop relative-task rerun | Vivian | `results/vivian-4090/pilot_shop_rerun/` |
| ✅ | Main guard comparison matrix and scenarios | Vivian | `experiments/main/matrix.json` |
| ✅ | Change-timing study matrix | Vivian | `experiments/main/matrix_timing.json` |
| ❌ | Run the main guard comparison on inbox and shop | Vivian | `results/vivian-4090/` |
| ❌ | Run the change-timing study (before screenshot vs. between screenshot and action) | Vivian | `results/vivian-4090/` |
| ❌ | Change-kind and task-kind breakdowns of the main results | Vivian | `results/vivian-4090/` |
| ❌ | Second-family experiments: main matrices rerun with InternVL3.5 as executor | Guru | `results/guru-4500/` |
| ❌ | Guard comparison on the files, tickets, calendar and chat domains | Guru | `results/guru-4500/` |

## Phase 10: Reports, docs and release (M11)

| Status | Task | Owner | Where |
|---|---|---|---|
| ✅ | Report builder that reads result files | Vivian | `src/stalehand/report/` |
| ✅ | Results explorer: static site that reads and validates result JSONL | Guru | `site/` |
| ❌ | Combined final report across both machines' results | Vivian | `src/stalehand/report/` |
| ❌ | Charts for the main results (guard vs. stale rate, false alarms, cost) | Guru | `site/` |
| ❌ | Results section in `README.md`, generated from result files | Guru | `README.md` |
| ❌ | Usage guide: generate scenarios, serve models, run a matrix, build a report | Guru | `docs/` |
| ❌ | Worked examples (one scenario end to end, adding a new domain) | Guru | `docs/`, `examples/` |
| ❌ | Choose a license before the repository is made public | Vivian | `LICENSE` |
| ❌ | Decide whether to add a real application (for example a self-hosted mail client) | Guru | `docs/design.md` |

## Who does what next

| # | Vivian | Guru |
|---|---|---|
| 1 | ❌ Static render mode | ❌ Second-family experiments |
| 2 | ❌ Full cost accounting | ❌ Guard comparison on the four new domains |
| 3 | ❌ Run the main guard comparison | ❌ Charts for the main results |
| 4 | ❌ Run the change-timing study | ❌ README results section |
| 5 | ❌ Change-kind and task-kind breakdowns | ❌ Usage guide |
| 6 | ❌ Combined final report | ❌ Worked examples |
| 7 | ❌ Choose a license | ❌ Real-application decision |

Guru's second-family runs depend on Vivian's main guard comparison config; Guru's charts and README section
depend on the main results landing.

## Hardware

| Person | Machines | Used for |
|---|---|---|
| Vivian | two lab RTX 4090 boxes (24 GB each), a lab box with 4x GTX 1080 (8 GB each, no bf16), laptop | inbox and shop experiments, pilot replication; the 1080s take models up to about 2B, quantized arms and CPU or browser work |
| Guru | RTX 4500 Ada workstation | new domains, second model family, results site |

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
