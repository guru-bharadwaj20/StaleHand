# StaleHand design

## Problem

Many computer-use agents split the work between two models. A planner (or orchestrator) looks at the screen and
writes a subtask in words; an executor carries the subtask out over one or more steps. If the screen changes after
the subtask was written, the words can point at the wrong thing.

Our pilot (Sep 2026, synthetic inbox, Qwen3-VL-8B planner, UI-TARS-1.5-7B executor) showed the sharpest form of
this. Given "forward the latest email from Samuel Lee", the planner names that email's subject. When a newer email
from Samuel Lee arrives, the executor follows the subject line and opens the old email: 0-5% correct, against
92.5-100% when the planner re-reads the screen. Giving the executor the user's task as well did not help.

Two published lines of work sit next to this:

- Time-of-check/time-of-use attacks on browser and desktop agents (arXiv 2603.00476, 2604.18860). They cover the
  few seconds between a screenshot and the action that follows it, and defend by blocking the action when the page
  changed. They do not measure how often that blocks harmless changes, and they do not cover a subtask that stays
  in force for several steps.
- Agent S3 (arXiv 2510.02250) dropped its planner and gained 9.1 OSWorld points. Delegating frameworks such as
  CoAct-1 (arXiv 2508.03923) still hand a written subtask to a GUI operator that runs up to 25 steps alone.

StaleHand is the missing piece between them: a reproducible test suite for multi-step subtask handoffs under
screen changes, and a fair comparison of the guards that can protect them.

## Questions the project answers

1. How often does each agent architecture act on a stale target when the screen changes mid-subtask?
2. Which guard keeps the agent correct, and what does it cost in false alarms on harmless changes, extra planner
   calls and time?
3. Does the answer depend on the kind of change (new item on top, re-sort, value update, target removed, cosmetic
   banner) and on the kind of task (fixed target or relative reference such as "latest" or "cheapest")?

## Architecture

```
scenarios ──► apps (HTML/JS) ──► env (Playwright) ◄──► agents (planner + executor) ◄── guards
    │                                   │                        │
    └──────────── ground truth ─────────┴──── episode log ───────┴──► metrics ──► reports
```

| Package | Responsibility |
|---|---|
| `stalehand.scenarios` | Pure data. Items, the task's selection criterion, change events, and a resolver that computes the correct target for any list of items. Deterministic from a seed. |
| `stalehand.apps` | One small web app per domain (inbox, shop, files, tickets, calendar, chat). Items carry `data-item-id`, and every user action is logged. Changes are applied live through a JavaScript hook. |
| `stalehand.env` | A Playwright environment around an app: reset, screenshot, act, apply a change at a set step, and report DOM mutations. A static mode renders before and after screens for cheap single-step runs. |
| `stalehand.models` | One interface for vision-language models: local transformers, an OpenAI-compatible server (vLLM), and a scripted fake for tests. Output parsers live with each model family. |
| `stalehand.agents` | Three architectures: hierarchical (planner and worker, Agent S2 style), delegated (orchestrator and GUI operator with a step budget and summary, CoAct-1 style) and flat (one policy per step, Agent S3 style, as a reference). |
| `stalehand.guards` | Hooks that run before each executor action: none, re-plan every step, self-check, rule subtask, DOM-change abort, pixel-diff abort, and target re-binding. |
| `stalehand.metrics` | Per-episode outcomes and paired statistics (exact McNemar, cluster bootstrap over scenario templates). |
| `stalehand.runner` | Expands a config into a run matrix, shards it across machines, writes JSONL results with the full config, seed and library versions, and resumes after a crash. |
| `stalehand.report` | Tables and charts from result files only. |

## Ground truth

The correct target is computed, never hand-labelled. A task has a criterion: equality filters (for example
`sender == "Samuel Lee"`) and, for relative tasks, an ordering (`received_at`, newest first). The resolver applies
the criterion to the items on screen at the moment of the committing action. The stale target is the resolver's
answer on the screen the planner saw. A change is relevant exactly when the two answers differ; this is computed
from the data too.

## Outcomes per episode

- `success`: the committing action (send, buy, delete, open) hit the correct target and the flow finished.
- `stale_action`: the committing action hit the stale target.
- `false_alarm`: a guard stopped or re-planned although the change was irrelevant or there was no change.
- `planner_calls`, `executor_calls`, `steps`, `seconds`.

## Guards

| Guard | What it does before an executor action | Expected weakness |
|---|---|---|
| none | nothing | acts on stale targets |
| replan_every_step | asks the planner for a fresh subtask | one planner call per step |
| self_check | asks the executor whether the subtask still fits the screen; re-plans on STALE | caught 9-26% of stale subtasks in the pilot |
| rule_subtask | the planner writes the target as a rule in the task's words; the executor resolves it on the live screen | lost about 8 points on fixed-target tasks in the pilot |
| dom_abort | blocks the action if the DOM changed since the subtask was written (as in arXiv 2603.00476) | fires on harmless changes; needs DOM access |
| pixel_abort | blocks the action if the screenshot changed beyond a threshold (as in arXiv 2604.18860) | fires on harmless changes |
| rebind | binds the subtask to an item, re-resolves the rule on each step, re-plans only if the binding moved | new; to be tested |

## Rules for results

- Every run writes its seed, config, model revisions and library versions next to its results.
- No number goes into a report unless a result file produced it.
- Negative results are reported as they are.
- Comparisons between guards use the same scenarios, models and decoding settings.

## Out of scope for now

Real third-party websites, training models, and human studies. These can follow once the suite is stable.
