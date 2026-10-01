Built from 2190 episodes. Click loop: the episode hit the step limit and its last four actions were clicks within 15 px of one spot.

| run set | architecture | guard | episodes | no commit | ran out of steps | click loop | click loop among no commit |
|---|---|---|---|---|---|---|---|
| main | hierarchical | replan_every_step | 205 | 14% | 40% | 5% | 38% |
| main | hierarchical | rebind_step | 205 | 30% | 52% | 41% | 82% |
| main | hierarchical | pixel_0.02_replan | 205 | 21% | 43% | 22% | 89% |
| main | hierarchical | rebind_dom | 205 | 27% | 53% | 41% | 73% |
| main | hierarchical | self_check | 205 | 28% | 33% | 20% | 66% |
| main | hierarchical | rule_subtask | 205 | 38% | 64% | 26% | 44% |
| main | hierarchical | none | 205 | 29% | 33% | 19% | 63% |
| main | hierarchical | dom_subtask_replan | 205 | 28% | 34% | 21% | 66% |
| pilot | hierarchical | replan_every_step | 205 | 25% | 50% | 12% | 47% |
| pilot | hierarchical | none | 205 | 46% | 51% | 27% | 57% |
| pilot_shop_rerun | hierarchical | replan_every_step | 70 | 0% | 0% | 0% | n/a |
| pilot_shop_rerun | hierarchical | none | 70 | 34% | 36% | 6% | 17% |
