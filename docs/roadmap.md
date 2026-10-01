# Roadmap

Each milestone ends with tests passing and a short note in `docs/progress.md`. Commit counts are budgets for
planning; every commit is one real change (see `CONTRIBUTING.md`).

| # | Milestone | Main output | Commits |
|---|---|---|---|
| M1 | Scenario core | items, criteria, resolver, change events, relevance, inbox and shop generators, JSONL export, CLI | 45 |
| M2 | Web apps | inbox and shop apps with multi-step flows, action log, live change hook, shared style kit | 50 |
| M3 | Environment | Playwright env, screenshot and action API, change scheduling, DOM mutation log, static render mode | 40 |
| M4 | Model backends | model interface, transformers backend, OpenAI-compatible backend, scripted fake, action and subtask parsers | 40 |
| M5 | Agent architectures | hierarchical, delegated and flat agents, episode loop, budgets, trajectory logging | 45 |
| M6 | Guards | the seven guards, each with unit tests on scripted models | 50 |
| M7 | Metrics and statistics | outcome classifier, McNemar, cluster bootstrap, cost accounting, summary tables | 35 |
| M8 | Runner | config schema, run matrix, sharding across GPU boxes, resume, provenance capture | 35 |
| M9 | More domains | files, tickets, calendar and chat apps and generators; change kinds per domain | 50 |
| M10 | Experiments | pilot replication, main guard comparison, change-kind and task-kind breakdowns, result files | 40 |
| M11 | Reports and docs | report builder, charts, README results, usage guide, examples | 30 |
| | **Total** | | **460** |

## Milestone gates

- **After M3:** a scripted agent can finish a forward-the-email flow in the live inbox, and a change applied at
  step 2 shows up in the screenshot and the DOM log.
- **After M5:** the pilot result reproduces in the live environment with the real models (stale subtask well below
  fresh subtask on relative tasks). If it does not, stop and find out why before building guards.
- **After M7:** every number in a summary table can be traced to a JSONL row.

## Open decisions

- License, before the repository is made public.
- Whether to add a real application (for example a self-hosted mail client) after M10.
