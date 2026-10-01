Built from 2190 episodes. Click loop: the episode hit the step limit and its last four actions were clicks within 15 px of one spot.

| run set | architecture | guard | episodes | no commit | ran out of steps | click loop |
|---|---|---|---|---|---|---|
| main | hierarchical | replan_every_step | 205 | 14% | 40% | 5% |
| main | hierarchical | rebind_step | 205 | 30% | 52% | 41% |
| main | hierarchical | pixel_0.02_replan | 205 | 21% | 43% | 22% |
| main | hierarchical | rebind_dom | 205 | 27% | 53% | 41% |
| main | hierarchical | self_check | 205 | 28% | 33% | 20% |
| main | hierarchical | rule_subtask | 205 | 38% | 64% | 26% |
| main | hierarchical | none | 205 | 29% | 33% | 19% |
| main | hierarchical | dom_subtask_replan | 205 | 28% | 34% | 21% |
| pilot | hierarchical | replan_every_step | 205 | 25% | 50% | 12% |
| pilot | hierarchical | none | 205 | 46% | 51% | 27% |
| pilot_shop_rerun | hierarchical | replan_every_step | 70 | 0% | 0% | 0% |
| pilot_shop_rerun | hierarchical | none | 70 | 34% | 36% | 6% |
