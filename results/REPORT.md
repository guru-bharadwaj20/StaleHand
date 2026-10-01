# StaleHand results

<!-- Rendered by `stalehand final` from docs/report_template.md. Edit the template, not results/REPORT.md.
Every number below is filled in from result files; the tables it links to are generated the same way. -->

All runs used Qwen3-VL-8B as planner and UI-TARS-1.5-7B as executor, in bf16 on two lab RTX 4090s, with greedy
decoding and seed 0. Each run directory holds the job, model revisions, git commit and library versions in
`config.json`. Intervals are 95% bootstrap intervals over scenario templates. p-values are exact McNemar tests on
paired episodes, Holm-adjusted within each family of comparisons.

## The problem is real: a subtask written before a change goes stale

In the main comparison (1640 episodes on the inbox and the shop), the planner writes a subtask from
one screen and the page changes before the executor looks at it. With no guard, the agent completed
4% of the 55 episodes whose change moved or removed the planner's
target, and acted on the stale target in 44% of them. On the 145
episodes where nothing relevant changed, the same agent succeeded 69% of the time. That
gap is the cost of a stale handoff.

| What the planner saw | What the executor saw |
|---|---|
| ![Inbox before the change](figures/inbox-relative-000-L1-planner.png) | ![Inbox after the change](figures/inbox-relative-000-L1-changed.png) |
| ![Shop before the change](figures/shop-cheapest-000-L1-planner.png) | ![Shop after the change](figures/shop-cheapest-000-L1-changed.png) |

Two of the main scenarios, drawn with `stalehand render`. Task: reply to the most recent email from Rohan Gupta. A
newer one arrives after the planner has picked the older one. Task: add the cheapest USB-C cable to the cart. The
listing changes and a cheaper cable appears.

## Every guard helps; they differ in what they cost

Paired on the same relevant-change scenarios, every guard beat no guard (`results/vivian-4090/main_report.md`,
"Paired against `none`"). The useful question is what each one costs in false alarms and model calls.

- **Re-planning at every step** had the highest success on relevant changes,
  80% (+76 pts over no guard,
  [+62, +90]). It fires on every step by design, so its false-alarm rate is
  100%, and it made 7.5 planner and checker calls
  per episode against 2.3 for no guard.
- **Re-binding on a DOM change** (`rebind_dom`) reached 55%
  (+51 pts, [+33, +68]) with 2.8 calls per
  episode. It fired on 15% of harmless changes, the lowest of the guards that watch the
  page, and kept success on harmless episodes at 68%.
- **Re-planning on a DOM change** (`dom_subtask_replan`) did about as well on relevant changes,
  58%, but fired on 76% of harmless
  changes, because any DOM change triggers it.
- **The pixel guard** fired on 100% of harmless changes. At the handoff it can't
  tell a harmless change from a relevant one, which matches the model-free calibration in
  `results/vivian-4090/checks_report.md`. It works as an expensive version of re-planning every step.
- **Self-check** reached 36% at 9.2 calls per episode.
- **Rule subtasks** gained the least, 27% on relevant changes, and lowered
  success on harmless ones to 50%. Writing the subtask as a rule seems to make
  the executor's job harder even when nothing changes.

## A confound: the executor gets stuck clicking one spot

With no guard, 63% of the episodes that ended without committing were click loops:
the episode ran out of steps while the executor clicked the same spot (`results/vivian-4090/loops_report.md`).
Usually the click had already worked. The page moved on, and the executor kept clicking a label that looks like the
button it was told to press. A plain hierarchical executor only hands control back when it says it is finished, so
the planner never sees the new screen. Re-planning at every step asks the planner at every step anyway, and its
episodes were click loops 5% of the time, against 19% with
no guard. Part of its lead over the cheaper guards may therefore come from breaking loops rather than from catching
stale subtasks. `docs/progress.md` has the details.
