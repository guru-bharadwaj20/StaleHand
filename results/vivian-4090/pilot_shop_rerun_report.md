Built from 140 scored episodes.

## Outcomes

| architecture | guard | domain | kind | change | n | success | stale | wrong_item | wrong_detail | aborted | no_commit | planner calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hierarchical | replan_every_step | shop | cheapest | none | 10 | 40% | 0% | 60% | 0% | 0% | 0% | 3.0 |
| hierarchical | replan_every_step | shop | cheapest | irrelevant | 5 | 40% | 0% | 60% | 0% | 0% | 0% | 3.0 |
| hierarchical | replan_every_step | shop | cheapest | relevant | 20 | 25% | 30% | 45% | 0% | 0% | 0% | 3.2 |
| hierarchical | replan_every_step | shop | highest_rated | irrelevant | 10 | 70% | 0% | 30% | 0% | 0% | 0% | 3.0 |
| hierarchical | replan_every_step | shop | highest_rated | relevant | 15 | 20% | 53% | 27% | 0% | 0% | 0% | 3.5 |
| hierarchical | replan_every_step | shop | highest_rated | none | 10 | 80% | 0% | 20% | 0% | 0% | 0% | 3.0 |
| hierarchical | none | shop | cheapest | relevant | 20 | 10% | 20% | 20% | 0% | 0% | 50% | 2.0 |
| hierarchical | none | shop | cheapest | none | 10 | 20% | 0% | 40% | 0% | 0% | 40% | 2.0 |
| hierarchical | none | shop | cheapest | irrelevant | 5 | 40% | 0% | 40% | 0% | 0% | 20% | 2.4 |
| hierarchical | none | shop | highest_rated | relevant | 15 | 0% | 53% | 20% | 0% | 0% | 27% | 2.5 |
| hierarchical | none | shop | highest_rated | irrelevant | 10 | 70% | 0% | 20% | 0% | 0% | 10% | 2.8 |
| hierarchical | none | shop | highest_rated | none | 10 | 50% | 0% | 10% | 0% | 0% | 40% | 2.2 |

## False alarms on harmless changes

| architecture | guard | episodes | false alarm rate | planner calls |
|---|---|---|---|---|
| hierarchical | replan_every_step | 70 | 100% | 3.2 |
| hierarchical | none | 70 | 0% | 2.3 |

## Paired against `none` on relevant changes

Same scenarios in both arms. Difference is the guard's success rate minus the baseline's, with a 95% bootstrap interval over scenario templates (10000 resamples, seed 0) and an exact McNemar test on the discordant pairs.

| architecture | guard | domain | pairs | none | guard | difference | 95% CI | only guard vs only baseline succeeded | McNemar |
|---|---|---|---|---|---|---|---|---|---|
| hierarchical | replan_every_step | shop | 35 | 6% | 23% | +17 pts | [+8, +26] | 6 vs 0 | p = 0.031 |
| hierarchical | replan_every_step | all | 35 | 6% | 23% | +17 pts | [+8, +26] | 6 vs 0 | p = 0.031 |
