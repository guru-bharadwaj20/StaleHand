# StaleHand results

<!-- Rendered by `stalehand final` from docs/report_template.md. Edit the template, not results/REPORT.md.
Every number below is filled in from result files; the tables it links to are generated the same way. -->

All runs used Qwen3-VL-8B as planner and UI-TARS-1.5-7B as executor, in bf16 on two lab RTX 4090s, with greedy
decoding and seed 0. Each run directory holds the job, model revisions, git commit and library versions in
`config.json`. Intervals are 95% bootstrap intervals over scenario templates. p-values are exact McNemar tests on
paired episodes, Holm-adjusted within each family of comparisons.

## The problem is real: a subtask written before a change goes stale

In the main comparison ({{main.episodes}} episodes on the inbox and the shop), the planner writes a subtask from
one screen and the page changes before the executor looks at it. With no guard, the agent completed
{{main.none.relevant_success}} of the {{main.none.relevant_n}} episodes whose change moved or removed the planner's
target, and acted on the stale target in {{main.none.relevant_stale}} of them. On the {{main.none.harmless_n}}
episodes where nothing relevant changed, the same agent succeeded {{main.none.harmless_success}} of the time. That
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
  {{main.replan_every_step.relevant_success}} ({{main.replan_every_step.vs_none.diff}} over no guard,
  {{main.replan_every_step.vs_none.ci}}). It fires on every step by design, so its false-alarm rate is
  {{main.replan_every_step.false_alarm}}, and it made {{main.replan_every_step.calls}} planner and checker calls
  per episode against {{main.none.calls}} for no guard.
- **Re-binding on a DOM change** (`rebind_dom`) reached {{main.rebind_dom.relevant_success}}
  ({{main.rebind_dom.vs_none.diff}}, {{main.rebind_dom.vs_none.ci}}) with {{main.rebind_dom.calls}} calls per
  episode. It fired on {{main.rebind_dom.false_alarm}} of harmless changes, the lowest of the guards that watch the
  page, and kept success on harmless episodes at {{main.rebind_dom.harmless_success}}. It fired on
  {{main.rebind_dom.relevant_fired}} of the relevant changes, so detection is not what holds it back; the next
  section is.
- **Re-planning on a DOM change** (`dom_subtask_replan`) did about as well on relevant changes,
  {{main.dom_subtask_replan.relevant_success}}, but fired on {{main.dom_subtask_replan.false_alarm}} of harmless
  changes, because any DOM change triggers it.
- **The pixel guard** fired on {{main.pixel_0.02_replan.false_alarm}} of harmless changes. At the handoff it can't
  tell a harmless change from a relevant one, which matches the model-free calibration in
  `results/vivian-4090/checks_report.md`. It works as an expensive version of re-planning every step.
- **Self-check** reached {{main.self_check.relevant_success}} at {{main.self_check.calls}} calls per episode.
- **Rule subtasks** gained the least, {{main.rule_subtask.relevant_success}} on relevant changes, and lowered
  success on harmless ones to {{main.rule_subtask.harmless_success}}. Writing the subtask as a rule seems to make
  the executor's job harder even when nothing changes.

## A confound: the executor gets stuck clicking one spot

With no guard, {{main.none.loop_among_no_commit}} of the episodes that ended without committing were click loops:
the episode ran out of steps while the executor clicked the same spot (`results/vivian-4090/loops_report.md`).
Usually the click had already worked. The page moved on, and the executor kept clicking a label that looks like the
button it was told to press. A plain hierarchical executor only hands control back when it says it is finished, so
the planner never sees the new screen. Re-planning at every step asks the planner at every step anyway, and its
episodes were click loops {{main.replan_every_step.click_loop}} of the time, against {{main.none.click_loop}} with
no guard. Part of its lead over the cheaper guards may therefore come from breaking loops rather than from catching
stale subtasks. `docs/progress.md` has the details.
