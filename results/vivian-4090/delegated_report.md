Built from 820 scored episodes.

![Success against false alarms (delegated)](delegated_report_delegated_tradeoff.svg)

![Episodes with a relevant change (delegated)](delegated_report_delegated_outcomes.svg)

## Summary by guard

Relevant: the change moved or removed the target the planner saw. Harmless: no change, or one that leaves the target where it was. Fired: the guard re-planned, re-bound or aborted at least once. Calls: planner plus checker calls per episode.

| architecture | guard | relevant n | fired | success | stale | harmless n | success | false alarms | calls |
|---|---|---|---|---|---|---|---|---|---|
| delegated | dom_subtask_replan | 55 | 100% | 69% | 2% | 145 | 69% | 76% | 3.5 |
| delegated | none | 55 | 0% | 15% | 42% | 145 | 70% | 0% | 2.7 |
| delegated | rebind_dom | 55 | 93% | 67% | 0% | 145 | 63% | 16% | 3.2 |
| delegated | replan_every_step | 55 | 100% | 75% | 2% | 145 | 78% | 100% | 7.5 |

## By change kind

Success on each kind of change. When the change removed the target there is no correct item, so the column counts episodes that held off: no commit, or a guard abort.

| architecture | guard | no change | irrelevant | relevant | target removed: held off |
|---|---|---|---|---|---|
| delegated | dom_subtask_replan | 66% of 70 | 72% of 75 | 69% of 55 | 100% of 5 |
| delegated | none | 63% of 70 | 76% of 75 | 15% of 55 | 100% of 5 |
| delegated | rebind_dom | 63% of 70 | 64% of 75 | 67% of 55 | 80% of 5 |
| delegated | replan_every_step | 74% of 70 | 81% of 75 | 75% of 55 | 60% of 5 |

## Relevant changes by task

Success on episodes whose change moved the target, per task.

| architecture | guard | inbox relative | shop cheapest | shop highest_rated |
|---|---|---|---|---|
| delegated | dom_subtask_replan | 60% of 20 | 70% of 20 | 80% of 15 |
| delegated | none | 0% of 20 | 25% of 20 | 20% of 15 |
| delegated | rebind_dom | 60% of 20 | 75% of 20 | 67% of 15 |
| delegated | replan_every_step | 75% of 20 | 70% of 20 | 80% of 15 |

## Outcomes

| architecture | guard | domain | kind | change | n | success | stale | wrong_item | wrong_detail | aborted | no_commit | planner calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| delegated | none | inbox | fixed | irrelevant | 30 | 70% | 0% | 0% | 0% | 0% | 30% | 2.4 |
| delegated | none | inbox | fixed | none | 20 | 70% | 0% | 0% | 0% | 0% | 30% | 2.3 |
| delegated | none | inbox | relative | irrelevant | 10 | 80% | 0% | 0% | 0% | 0% | 20% | 2.5 |
| delegated | none | inbox | relative | none | 20 | 60% | 0% | 0% | 0% | 0% | 40% | 2.5 |
| delegated | none | inbox | relative | relevant | 20 | 0% | 70% | 0% | 0% | 0% | 30% | 2.5 |
| delegated | none | shop | cheapest | irrelevant | 5 | 20% | 0% | 80% | 0% | 0% | 0% | 2.8 |
| delegated | none | shop | cheapest | none | 10 | 20% | 0% | 80% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | cheapest | relevant | 20 | 25% | 15% | 60% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | fixed | irrelevant | 20 | 100% | 0% | 0% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | fixed | none | 10 | 90% | 0% | 10% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | fixed | target_removed | 5 | 0% | 0% | 0% | 0% | 0% | 100% | 2.2 |
| delegated | none | shop | highest_rated | irrelevant | 10 | 70% | 0% | 30% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | highest_rated | none | 10 | 70% | 0% | 30% | 0% | 0% | 0% | 3.0 |
| delegated | none | shop | highest_rated | relevant | 15 | 20% | 40% | 40% | 0% | 0% | 0% | 3.1 |
| delegated | dom_subtask_replan | inbox | fixed | irrelevant | 30 | 70% | 0% | 0% | 0% | 0% | 30% | 3.3 |
| delegated | dom_subtask_replan | inbox | fixed | none | 20 | 70% | 0% | 0% | 0% | 0% | 30% | 2.9 |
| delegated | dom_subtask_replan | inbox | relative | irrelevant | 10 | 50% | 0% | 10% | 0% | 0% | 40% | 3.5 |
| delegated | dom_subtask_replan | inbox | relative | none | 20 | 65% | 0% | 0% | 0% | 0% | 35% | 3.0 |
| delegated | dom_subtask_replan | inbox | relative | relevant | 20 | 60% | 0% | 0% | 0% | 0% | 40% | 3.5 |
| delegated | dom_subtask_replan | shop | cheapest | irrelevant | 5 | 40% | 0% | 60% | 0% | 0% | 0% | 3.8 |
| delegated | dom_subtask_replan | shop | cheapest | none | 10 | 30% | 0% | 70% | 0% | 0% | 0% | 3.5 |
| delegated | dom_subtask_replan | shop | cheapest | relevant | 20 | 70% | 5% | 25% | 0% | 0% | 0% | 3.9 |
| delegated | dom_subtask_replan | shop | fixed | irrelevant | 20 | 100% | 0% | 0% | 0% | 0% | 0% | 4.0 |
| delegated | dom_subtask_replan | shop | fixed | none | 10 | 90% | 0% | 10% | 0% | 0% | 0% | 3.5 |
| delegated | dom_subtask_replan | shop | fixed | target_removed | 5 | 0% | 0% | 0% | 0% | 0% | 100% | 3.2 |
| delegated | dom_subtask_replan | shop | highest_rated | irrelevant | 10 | 60% | 0% | 40% | 0% | 0% | 0% | 4.0 |
| delegated | dom_subtask_replan | shop | highest_rated | none | 10 | 70% | 0% | 30% | 0% | 0% | 0% | 3.5 |
| delegated | dom_subtask_replan | shop | highest_rated | relevant | 15 | 80% | 0% | 20% | 0% | 0% | 0% | 4.0 |
| delegated | rebind_dom | inbox | fixed | irrelevant | 30 | 70% | 0% | 7% | 0% | 0% | 23% | 2.3 |
| delegated | rebind_dom | inbox | fixed | none | 20 | 80% | 0% | 0% | 0% | 0% | 20% | 2.0 |
| delegated | rebind_dom | inbox | relative | irrelevant | 10 | 30% | 0% | 20% | 0% | 0% | 50% | 2.3 |
| delegated | rebind_dom | inbox | relative | none | 20 | 50% | 0% | 5% | 0% | 0% | 45% | 2.2 |
| delegated | rebind_dom | inbox | relative | relevant | 20 | 60% | 0% | 0% | 0% | 0% | 40% | 2.3 |
| delegated | rebind_dom | shop | cheapest | irrelevant | 5 | 40% | 0% | 60% | 0% | 0% | 0% | 2.8 |
| delegated | rebind_dom | shop | cheapest | none | 10 | 50% | 0% | 50% | 0% | 0% | 0% | 2.9 |
| delegated | rebind_dom | shop | cheapest | relevant | 20 | 75% | 0% | 25% | 0% | 0% | 0% | 2.7 |
| delegated | rebind_dom | shop | fixed | irrelevant | 20 | 65% | 0% | 0% | 0% | 0% | 35% | 2.3 |
| delegated | rebind_dom | shop | fixed | none | 10 | 40% | 0% | 10% | 0% | 0% | 50% | 2.4 |
| delegated | rebind_dom | shop | fixed | target_removed | 5 | 0% | 0% | 20% | 0% | 0% | 80% | 3.2 |
| delegated | rebind_dom | shop | highest_rated | irrelevant | 10 | 90% | 0% | 10% | 0% | 0% | 0% | 2.3 |
| delegated | rebind_dom | shop | highest_rated | none | 10 | 90% | 0% | 10% | 0% | 0% | 0% | 2.7 |
| delegated | rebind_dom | shop | highest_rated | relevant | 15 | 67% | 0% | 7% | 0% | 0% | 27% | 2.5 |
| delegated | replan_every_step | inbox | fixed | irrelevant | 30 | 80% | 0% | 0% | 0% | 0% | 20% | 9.0 |
| delegated | replan_every_step | inbox | fixed | none | 20 | 80% | 0% | 0% | 0% | 0% | 20% | 8.9 |
| delegated | replan_every_step | inbox | relative | irrelevant | 10 | 80% | 0% | 10% | 0% | 0% | 10% | 13.0 |
| delegated | replan_every_step | inbox | relative | none | 20 | 80% | 0% | 0% | 0% | 0% | 20% | 12.5 |
| delegated | replan_every_step | inbox | relative | relevant | 20 | 75% | 0% | 0% | 0% | 0% | 25% | 13.0 |
| delegated | replan_every_step | shop | cheapest | irrelevant | 5 | 60% | 0% | 40% | 0% | 0% | 0% | 4.0 |
| delegated | replan_every_step | shop | cheapest | none | 10 | 50% | 0% | 50% | 0% | 0% | 0% | 3.5 |
| delegated | replan_every_step | shop | cheapest | relevant | 20 | 70% | 5% | 25% | 0% | 0% | 0% | 4.0 |
| delegated | replan_every_step | shop | fixed | irrelevant | 20 | 100% | 0% | 0% | 0% | 0% | 0% | 4.0 |
| delegated | replan_every_step | shop | fixed | none | 10 | 90% | 0% | 10% | 0% | 0% | 0% | 3.5 |
| delegated | replan_every_step | shop | fixed | target_removed | 5 | 0% | 0% | 40% | 0% | 0% | 60% | 11.6 |
| delegated | replan_every_step | shop | highest_rated | irrelevant | 10 | 60% | 0% | 40% | 0% | 0% | 0% | 4.0 |
| delegated | replan_every_step | shop | highest_rated | none | 10 | 60% | 0% | 40% | 0% | 0% | 0% | 3.5 |
| delegated | replan_every_step | shop | highest_rated | relevant | 15 | 80% | 0% | 20% | 0% | 0% | 0% | 4.0 |

## Cost per episode

Means per episode. Model seconds add up the latency of every model call, so they include time spent waiting in a shared server's batch; compare them within one run set only.

| architecture | guard | planner calls | checker calls | executor calls | model seconds | actions |
|---|---|---|---|---|---|---|
| delegated | dom_subtask_replan | 3.5 | 0.0 | 7.0 | 96.9 | 5.7 |
| delegated | none | 2.7 | 0.0 | 6.9 | 87.9 | 5.5 |
| delegated | rebind_dom | 2.4 | 0.8 | 8.0 | 99.6 | 7.2 |
| delegated | replan_every_step | 7.5 | 0.0 | 6.0 | 150.9 | 6.0 |

## False alarms on harmless changes

| architecture | guard | harmless episodes | false alarm rate | planner calls |
|---|---|---|---|---|
| delegated | dom_subtask_replan | 145 | 76% | 3.5 |
| delegated | none | 145 | 0% | 2.7 |
| delegated | rebind_dom | 145 | 16% | 2.4 |
| delegated | replan_every_step | 145 | 100% | 7.5 |

## Paired against `none` on relevant changes

Same scenarios in both arms. Difference is the guard's success rate minus the baseline's, with a 95% bootstrap interval over scenario templates (10000 resamples, seed 0) and an exact McNemar test on the discordant pairs.

| architecture | guard | domain | pairs | none | guard | difference | 95% CI | only guard vs only baseline succeeded | McNemar |
|---|---|---|---|---|---|---|---|---|---|
| delegated | dom_subtask_replan | shop | 35 | 23% | 74% | +51 pts | [+37, +65] | 18 vs 0 | p < 0.001 |
| delegated | dom_subtask_replan | inbox | 20 | 0% | 60% | +60 pts | [+30, +90] | 12 vs 0 | p < 0.001 |
| delegated | dom_subtask_replan | all | 55 | 15% | 69% | +55 pts | [+40, +69] | 30 vs 0 | p < 0.001 |
| delegated | replan_every_step | shop | 35 | 23% | 74% | +51 pts | [+37, +65] | 18 vs 0 | p < 0.001 |
| delegated | replan_every_step | inbox | 20 | 0% | 75% | +75 pts | [+55, +95] | 15 vs 0 | p < 0.001 |
| delegated | replan_every_step | all | 55 | 15% | 75% | +60 pts | [+47, +73] | 33 vs 0 | p < 0.001 |
| delegated | rebind_dom | shop | 35 | 23% | 71% | +49 pts | [+35, +61] | 20 vs 3 | p < 0.001 |
| delegated | rebind_dom | inbox | 20 | 0% | 60% | +60 pts | [+35, +85] | 12 vs 0 | p < 0.001 |
| delegated | rebind_dom | all | 55 | 15% | 67% | +53 pts | [+40, +66] | 32 vs 3 | p < 0.001 |
