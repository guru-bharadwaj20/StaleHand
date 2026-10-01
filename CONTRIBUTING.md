# Contributing

## Task split

Two people work on this repository: Vivian and Guru. The split follows directories, so each person can work and
merge without waiting on the other. ✅ means done and merged; ❌ means still to do.

### Hardware

| Person | Machines | Used for |
|---|---|---|
| Vivian | two lab RTX 4090 boxes (24 GB each), laptop | inbox and shop experiments, pilot replication |
| Guru | RTX 4500 Ada workstation | new domains, second model family, results site |

Runs stay on their owner's machines and write to separate result directories (`results/vivian-4090/`,
`results/guru-4500/`), so no two runs ever write the same file.

### Vivian: core pipeline, runner, inbox and shop experiments

| Status | Task | Where |
|---|---|---|
| ✅ | Scenario core: items, criteria, resolver, change events, relevance | `src/stalehand/scenarios/` |
| ✅ | Inbox and shop scenario generators, JSONL export, `stalehand scenarios` command | `src/stalehand/scenarios/domains/`, `src/stalehand/cli.py` |
| ✅ | Scenario and result JSON schemas, shared fixtures | `schema/` |
| ✅ | Inbox and shop web apps, page harness, bundler | `apps/src/{core,inbox,shop}/`, `apps/build.mjs` |
| ✅ | Playwright environment: actions, change timing, DOM mutation tracking, event steps | `src/stalehand/env/` |
| ✅ | Model backends (scripted, OpenAI-compatible, transformers) and output parsers | `src/stalehand/models/` |
| ✅ | Hierarchical planner-executor agent and trajectory log | `src/stalehand/agents/` |
| ✅ | Guards: re-plan every step, self-check, rule subtask, DOM change, pixel change | `src/stalehand/guards/` |
| ✅ | Episode outcome scoring | `src/stalehand/metrics/outcome.py` |
| ✅ | `screendiff` crate: pixel difference and SSIM | `crates/screendiff/` |
| ✅ | Go runner: matrix, SQLite job store, ssh dispatch, `stalerun` command | `runner/` |
| ❌ | `stalehand run-job` command, the entry point the Go runner calls | `src/stalehand/cli.py`, `src/stalehand/run/` |
| ❌ | Delegated agent (orchestrator and GUI operator, CoAct-1 style) | `src/stalehand/agents/delegated.py` |
| ❌ | Flat agent (one policy per step, Agent S3 style), as a reference | `src/stalehand/agents/flat.py` |
| ❌ | Rebind guard: re-resolve the rule each step, re-plan only if the target moved | `src/stalehand/guards/rebind.py` |
| ✅ | Paired statistics: exact McNemar, cluster bootstrap over scenario templates | `src/stalehand/metrics/stats.py` |
| ❌ | Runner provenance (git commit, model revisions, library versions) and result collection | `runner/`, `src/stalehand/run/` |
| ❌ | Model serving scripts for the lab boxes | `scripts/lab/` |
| ❌ | Pilot replication in the live environment (gate: stale subtask well below fresh on relative tasks) | `results/vivian-4090/` |
| ❌ | Main guard comparison on inbox and shop | `results/vivian-4090/` |
| ❌ | Change-timing study: changes before the screenshot against changes between screenshot and action | `results/vivian-4090/` |
| ❌ | Report builder that reads result files | `src/stalehand/report/` |

### Guru: new domains, statistics crate, second model family, results site

| Status | Task | Where |
|---|---|---|
| ✅ | Files domain: generator, app and browser tests ("share the newest report"; uploads, renames) | `src/stalehand/scenarios/domains/files.py`, `apps/src/files/`, `tests/` |
| ✅ | Tickets domain ("assign the oldest high-priority ticket"; new tickets, priority changes) | `.../domains/tickets.py`, `apps/src/tickets/` |
| ✅ | Calendar domain ("join the next meeting with Kenji"; reschedules, cancellations) | `.../domains/calendar.py`, `apps/src/calendar/` |
| ❌ | Chat domain ("reply to the latest message from Grace"; new and edited messages) | `.../domains/chat.py`, `apps/src/chat/` |
| ❌ | `stalestats` crate: cluster bootstrap and exact McNemar over result JSONL, checked against the Python version on the same files | `crates/stalestats/` |
| ❌ | Model serving on the RTX 4500 Ada (vLLM, OpenAI-compatible endpoint) | `scripts/ada/` |
| ❌ | Second executor family (a different open GUI model) wired into the model registry | `src/stalehand/models/registry.py` (new entries only) |
| ❌ | Second-family experiments: the main matrices rerun with the other executor family | `results/guru-4500/` |
| ❌ | Results explorer: static TypeScript site that reads result JSONL and validates it against `schema/result.schema.json` | `site/` |

### Keeping the two halves independent

- **Contracts.** The halves meet only at `schema/*.schema.json`, the `window.stalehand` page API
  (`apps/src/core/harness.ts`), the model interface (`src/stalehand/models/base.py`) and the guard interface
  (`src/stalehand/guards/base.py`). Changing a contract needs a pull request that both people approve.
- **No shared lists to edit.** New scenario domains are discovered from `scenarios/domains/`, and new apps from
  `apps/src/*/main.ts`, so adding a domain touches only new files.
- **Branches.** Work on `vivian/<topic>` or `guru/<topic>` and merge to `main` through a pull request with CI
  green. Rebase before merging; never force-push `main`.
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
