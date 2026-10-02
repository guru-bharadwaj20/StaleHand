# StaleHand results

<!-- Rendered by `stalehand final` from docs/report_template.md. Edit the template, not results/REPORT.md.
Every number below is filled in from result files; the tables it links to are generated the same way. -->

All runs used Qwen3-VL-8B as planner and UI-TARS-1.5-7B as executor, in bf16 on two lab RTX 4090s, with greedy
decoding and seed 0. Each run directory holds the job, model revisions, git commit and library versions in
`config.json`. Intervals are 95% bootstrap intervals over scenario templates. p-values are exact McNemar tests on
paired episodes, Holm-adjusted within each family of comparisons.

## A subtask written before a change goes stale

In the main comparison ({{main.episodes}} episodes on the inbox and the shop), the planner writes a subtask from
one screen and the page changes before the executor looks at it. With no guard, the agent completed
{{main.none.relevant_success}} of the {{main.none.relevant_n}} episodes whose change moved or removed the planner's
target, and acted on the stale target in {{main.none.relevant_stale}} of them. On the {{main.none.harmless_n}}
episodes where nothing relevant changed, the same agent succeeded {{main.none.harmless_success}} of the time.

| What the planner saw | What the executor saw |
|---|---|
| ![Inbox before the change](figures/inbox-relative-000-L1-planner.png) | ![Inbox after the change](figures/inbox-relative-000-L1-changed.png) |
| ![Shop before the change](figures/shop-cheapest-000-L1-planner.png) | ![Shop after the change](figures/shop-cheapest-000-L1-changed.png) |

Two of the main scenarios, drawn with `stalehand render`. Task: reply to the most recent email from Rohan Gupta. A
newer one arrives after the planner has picked the older one. Task: add the cheapest USB-C cable to the cart. The
listing changes and a cheaper cable appears.

## Every guard helps, at different costs

Paired on the same relevant-change scenarios, every guard beat no guard (`results/vivian-4090/main_report.md`,
"Paired against `none`"). They differ in how often they fire when nothing relevant changed, and in how many model
calls they add.

- **Re-planning at every step** had the highest success on relevant changes,
  {{main.replan_every_step.relevant_success}} ({{main.replan_every_step.vs_none.diff}} over no guard,
  {{main.replan_every_step.vs_none.ci}}). It fires on every step by design, so its false-alarm rate is
  {{main.replan_every_step.false_alarm}}, and it made {{main.replan_every_step.calls}} planner and checker calls
  per episode against {{main.none.calls}} for no guard.
- **Re-binding on a DOM change** (`rebind_dom`) reached {{main.rebind_dom.relevant_success}}
  ({{main.rebind_dom.vs_none.diff}}, {{main.rebind_dom.vs_none.ci}}) with {{main.rebind_dom.calls}} calls per
  episode. It fired on {{main.rebind_dom.false_alarm}} of harmless changes, the lowest of the guards that watch the
  page, and kept success on harmless episodes at {{main.rebind_dom.harmless_success}}. It fired on
  {{main.rebind_dom.relevant_fired}} of the relevant changes, so it usually noticed them; many of its failures
  after that were the click loops described next.
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

## When the change lands mid-step, only a check right before the click helps

The timing study ({{timing.episodes}} episodes) reruns the main scenarios with the change landing between the
executor's screenshot and its click, the time-of-check to time-of-use window. The executor then clicks a position
taken from a screen that no longer exists.

The click usually lands on the wrong item, whether or not the change mattered to the task. On harmless changes,
the first item the agent opened was the wrong one in {{timing.none.first_open_missed}} of episodes with no guard,
against {{main.none.first_open_missed}} when the same change landed at the handoff
(`results/vivian-4090/recovery_report.md`). That matches the model-free click-hazard audit in
`results/vivian-4090/checks_report.md`.

What a guard can do about it depends on when it looks:

- **A DOM check just before the action** (`dom_step_replan`) sees the change before the click and re-plans. Its
  first-open misses stayed at {{timing.dom_step_replan.first_open_missed}}, and it reached
  {{timing.dom_step_replan.relevant_success}} on relevant changes ({{timing.dom_step_replan.vs_none.diff}} over no
  guard, {{timing.dom_step_replan.vs_none.ci}}) and {{timing.dom_step_replan.harmless_success}} on harmless ones.
- **A guard that checks only before the executor's next thought** comes in after the wrong click. Paired against
  the same guard under the handoff timing, `dom_subtask_replan` changed by {{timing.dom_subtask_replan.relevant.diff}}
  ({{timing.dom_subtask_replan.relevant.ci}}) on relevant changes and {{timing.dom_subtask_replan.harmless.diff}}
  ({{timing.dom_subtask_replan.harmless.ci}}) on harmless ones, and `rebind_step` by
  {{timing.rebind_step.relevant.diff}} and {{timing.rebind_step.harmless.diff}}. No guard changed by only
  {{timing.none.harmless.diff}} on harmless changes, so on those these guards did worse than having none. The miss
  itself is the same: the first opened item was wrong in {{timing.dom_subtask_replan.first_open_missed}} of
  harmless episodes with `dom_subtask_replan`, as with no guard. The difference is recovery. After a missed first
  click, no guard went on to succeed in {{timing.none.recovered}} of episodes and committed to a wrong item in
  {{timing.none.wrong_after_miss}}; `dom_subtask_replan` succeeded in {{timing.dom_subtask_replan.recovered}} and
  committed to a wrong item in {{timing.dom_subtask_replan.wrong_after_miss}}. In one trace we read in full, the
  re-plan starts from the wrong email's screen, and the new subtask ('Click the "Back to Inbox" button to return
  to the inbox and locate the email from Amara Okafor') has dropped the subject line that told the two emails
  apart. We have not checked how often that is the cause.
- **Aborting on any DOM change** (`dom_step_abort`) is a clean negative. It never acts on a stale target, but it
  succeeded on {{timing.dom_step_abort.relevant_success}} of relevant changes and
  {{timing.dom_step_abort.harmless_success}} of harmless ones, because nearly every episode sees some change.

Paired tables: `results/vivian-4090/contrasts_report.md` and `results/vivian-4090/timing_report.md`.

## Breaking executor loops closes most of the gap

The stall-return ablation ({{main_stall.episodes}} episodes) reruns three guards on the main scenarios with one
change to the agent: after two actions in a row that leave the screenshot unchanged, the executor hands control back
to the planner (architecture `hierarchical_stall`). The apps and scenarios are untouched, so every episode pairs
with its counterpart in the main comparison. A model-free check found no scenario whose correct flow would trip the
stall return (`results/vivian-4090/checks_report.md`).

- **`rebind_dom`** gained the most. On relevant changes it went from {{main.rebind_dom.relevant_success}} to
  {{main_stall.rebind_dom.relevant_success}} ({{main_stall.rebind_dom.relevant.diff}},
  {{main_stall.rebind_dom.relevant.ci}}, Holm {{main_stall.rebind_dom.relevant.p_holm}}). Its click loops fell
  from {{main.rebind_dom.click_loop}} to {{main_stall.rebind_dom.click_loop}} of episodes. The extra planner calls
  after a stall raised its cost from {{main.rebind_dom.calls}} to {{main_stall.rebind_dom.calls}} calls per
  episode. Its false alarms were {{main_stall.rebind_dom.false_alarm}} of harmless changes, against
  {{main.rebind_dom.false_alarm}} before.
- **Re-planning at every step** had little to gain, since it already escaped loops: {{main.replan_every_step.relevant_success}}
  to {{main_stall.replan_every_step.relevant_success}} on relevant changes ({{main_stall.replan_every_step.relevant.diff}},
  {{main_stall.replan_every_step.relevant.ci}}), still at {{main_stall.replan_every_step.calls}} calls per episode.
- **No guard** did better on harmless changes, {{main.none.harmless_success}} to {{main_stall.none.harmless_success}}
  ({{main_stall.none.harmless.diff}}, {{main_stall.none.harmless.ci}}, Holm {{main_stall.none.harmless.p_holm}}),
  but the stall return does nothing about staleness: it acted on the stale target in
  {{main_stall.none.relevant_stale}} of relevant changes.

With loops broken, `rebind_dom` reached {{main_stall.rebind_dom.relevant_success}} on relevant changes against
{{main_stall.replan_every_step.relevant_success}} for re-planning at every step, at {{main_stall.rebind_dom.calls}}
calls per episode instead of {{main_stall.replan_every_step.calls}}, and with false alarms on
{{main_stall.rebind_dom.false_alarm}} of harmless changes instead of all of them. We did not test the difference
between those two guards directly. In the main comparison, part of re-planning's lead came from loop escape.

## Delegating whole goals changes little

In the delegated architecture ({{delegated.episodes}} episodes) the orchestrator hands over a goal, and the operator
works on it alone for up to eight actions before reporting back. Paired with the hierarchical agent on the same
guard and scenarios, no difference survived the Holm adjustment (`results/vivian-4090/contrasts_report.md`). The
stale handoff is just as present: with no guard, the delegated agent succeeded on {{delegated.none.relevant_success}}
of relevant changes and acted on the stale target in {{delegated.none.relevant_stale}}. The guards help about as much
as before. `rebind_dom` gained {{delegated.rebind_dom.vs_none.diff}} over no guard ({{delegated.rebind_dom.vs_none.ci}})
and re-planning at every step {{delegated.replan_every_step.vs_none.diff}} ({{delegated.replan_every_step.vs_none.ci}}).
The operator's step budget also hands control back on its own, and click loops were rarer: {{delegated.none.click_loop}}
of episodes with no guard, against {{main.none.click_loop}} for the hierarchical agent.

## Without a planner, there is no stale subtask to follow

The flat reference ({{flat.episodes}} episodes) runs UI-TARS alone on the main scenarios: no planner and no guard.
It reads the task itself at every step, so no subtask can go stale. On relevant changes it succeeded
{{flat.none.relevant_success}} of the time and acted on the stale target in {{flat.none.relevant_stale}} of them,
against {{main.none.relevant_success}} and {{main.none.relevant_stale}} for the hierarchical agent with no guard
({{flat.none.relevant.diff}}, {{flat.none.relevant.ci}}, Holm {{flat.none.relevant.p_holm}}).

The timings are not quite matched. A flat agent has no handoff, so the change lands just before its first action,
which is what the mid-step timing does to the hierarchical agent. Its first-open misses on harmless changes,
{{flat.none.first_open_missed}}, match the mid-step run's {{timing.none.first_open_missed}}. Against that timing the
gap is about the same: the hierarchical agent with no guard succeeded on {{timing.none.relevant_success}} of
relevant changes and {{timing.none.harmless_success}} of harmless ones, the flat agent on
{{flat.none.relevant_success}} and {{flat.none.harmless_success}}. The guarded hierarchical agents still did better
than the flat one on relevant changes, as the main and stall sections show.

## A weaker planner goes stale about as often, and the guards still work

The small-planner run swaps Qwen3-VL-8B for Qwen3-VL-4B as the planner, keeps UI-TARS as the executor and runs four
guards on the main scenarios ({{small_planner.episodes}} episodes), so every row pairs with the main run. With no
guard the 4B planner's agent succeeded on {{small_planner.none.relevant_success}} of relevant changes and acted on the
stale target in {{small_planner.none.relevant_stale}}, against {{main.none.relevant_success}} and
{{main.none.relevant_stale}} with the 8B planner. It did worse on harmless changes:
{{small_planner.none.harmless_success}} against {{main.none.harmless_success}}
({{small_planner.none.harmless.diff}}, {{small_planner.none.harmless.ci}}, Holm {{small_planner.none.harmless.p_holm}}).

The guards help this planner too. On relevant changes `rebind_dom` reached {{small_planner.rebind_dom.relevant_success}}
({{small_planner.rebind_dom.vs_none.diff}} over no guard, {{small_planner.rebind_dom.vs_none.ci}}), re-planning at
every step {{small_planner.replan_every_step.relevant_success}} ({{small_planner.replan_every_step.vs_none.diff}},
{{small_planner.replan_every_step.vs_none.ci}}) and `dom_subtask_replan`
{{small_planner.dom_subtask_replan.relevant_success}} ({{small_planner.dom_subtask_replan.vs_none.diff}},
{{small_planner.dom_subtask_replan.vs_none.ci}}). The cheap guard costs more with the weaker planner: `rebind_dom`
raised a false alarm on {{small_planner.rebind_dom.false_alarm}} of harmless changes, against
{{main.rebind_dom.false_alarm}} with the 8B planner, and its harmless success was
{{small_planner.rebind_dom.harmless_success}} against {{main.rebind_dom.harmless_success}}.

## The new domains mostly measure whether the agent can do the task at all

The eight-guard run on calendar, chat, files and tickets finished ({{domains.episodes}} episodes). Most of it sits at
the floor. In the files domain the agent succeeded on {{domains.none.domain.files.success}} of
{{domains.none.domain.files.n}} episodes with no guard and {{domains.replan_every_step.domain.files.success}} with
re-planning at every step, and {{domains.none.domain.files.max_steps}} of the no-guard episodes ran out of steps.
Tickets fared about as badly: {{domains.none.domain.tickets.success}} with no guard and
{{domains.replan_every_step.domain.tickets.success}} with re-planning at every step. Chat reached
{{domains.none.domain.chat.success}} with no guard. In one files trace we read in full, the planner asks the executor
to click the file to open it, and the executor clicks the same spot until the step budget runs out; whether the files
and tickets apps support the action the planner asks for needs checking before these domains can say anything about
guards.

Calendar is the one domain where the comparison works. With no guard the agent succeeded on
{{domains.none.domain.calendar.success}} of {{domains.none.domain.calendar.n}} calendar episodes, with re-planning at
every step {{domains.replan_every_step.domain.calendar.success}}, with `dom_subtask_replan`
{{domains.dom_subtask_replan.domain.calendar.success}} and with `rebind_dom` {{domains.rebind_dom.domain.calendar.success}}.
Pooled over the four domains, the guards' gains on relevant changes were: re-planning at every step
{{domains.replan_every_step.vs_none.diff}} ({{domains.replan_every_step.vs_none.ci}}, Holm
{{domains.replan_every_step.vs_none.p_holm}}), `dom_subtask_replan` {{domains.dom_subtask_replan.vs_none.diff}}
({{domains.dom_subtask_replan.vs_none.ci}}, Holm {{domains.dom_subtask_replan.vs_none.p_holm}}) and `rebind_dom`
{{domains.rebind_dom.vs_none.diff}} ({{domains.rebind_dom.vs_none.ci}}, Holm {{domains.rebind_dom.vs_none.p_holm}}).
The earlier partial three-guard run (`domains_lab`) is superseded by this one.

## The second model family failed its check

Before running the main matrices with InternVL3.5-8B as the executor, we ran it alone on the main scenarios
({{flat_internvl.episodes}} episodes, no planner, as in the flat reference). It answered in UI-TARS's action format,
but the action parser could not read {{flat_internvl.none.parse_failures}} of its {{flat_internvl.none.executor_calls}}
replies, against {{flat.none.parse_failures}} for UI-TARS. The ones we looked at name a target without coordinates,
for example `click(start_box='Sneha Kulkarni')`. It succeeded on {{flat_internvl.none.harmless_success}} of harmless changes and
{{flat_internvl.none.relevant_success}} of relevant ones, against {{flat.none.harmless_success}} and
{{flat.none.relevant_success}} for UI-TARS alone. A stale-subtask comparison on top of an executor that cannot ground
would measure grounding, so the second-family runs were dropped. Mapping its named targets to page elements would
give it help UI-TARS does not get.

## Not run

- The main and mid-step matrices with InternVL3.5 as the executor (`experiments/second_family/`), dropped after the
  check above.
