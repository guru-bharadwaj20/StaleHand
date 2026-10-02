Built from 5109 episodes. Click loop: the episode hit the step limit and its last four actions were clicks within 15 px of one spot.

| run set | architecture | guard | episodes | no commit | ran out of steps | click loop | click loop among no commit |
|---|---|---|---|---|---|---|---|
| delegated | delegated | dom_subtask_replan | 205 | 19% | 24% | 3% | 5% |
| delegated | delegated | none | 205 | 18% | 23% | 1% | 6% |
| delegated | delegated | rebind_dom | 205 | 26% | 29% | 15% | 15% |
| delegated | delegated | replan_every_step | 205 | 11% | 40% | 2% | 17% |
| domains_lab | hierarchical | none | 97 | 76% | 79% | 39% | 51% |
| domains_lab | hierarchical | replan_every_step | 87 | 63% | 71% | 32% | 49% |
| domains_lab | hierarchical | rebind_dom | 70 | 63% | 63% | 40% | 64% |
| flat | flat | none | 205 | 17% | 40% | 5% | 12% |
| main | hierarchical | replan_every_step | 205 | 14% | 40% | 5% | 38% |
| main | hierarchical | rebind_step | 205 | 30% | 52% | 41% | 82% |
| main | hierarchical | pixel_0.02_replan | 205 | 21% | 43% | 22% | 89% |
| main | hierarchical | rebind_dom | 205 | 27% | 53% | 41% | 73% |
| main | hierarchical | self_check | 205 | 28% | 33% | 20% | 66% |
| main | hierarchical | rule_subtask | 205 | 38% | 64% | 26% | 44% |
| main | hierarchical | none | 205 | 29% | 33% | 19% | 63% |
| main | hierarchical | dom_subtask_replan | 205 | 28% | 34% | 21% | 66% |
| main_stall | hierarchical_stall | rebind_dom | 205 | 13% | 22% | 10% | 22% |
| main_stall | hierarchical_stall | replan_every_step | 205 | 9% | 40% | 2% | 21% |
| main_stall | hierarchical_stall | none | 205 | 17% | 20% | 6% | 35% |
| pilot | hierarchical | replan_every_step | 205 | 25% | 50% | 12% | 47% |
| pilot | hierarchical | none | 205 | 46% | 51% | 27% | 57% |
| pilot_shop_rerun | hierarchical | replan_every_step | 70 | 0% | 0% | 0% | n/a |
| pilot_shop_rerun | hierarchical | none | 70 | 34% | 36% | 6% | 17% |
| timing | hierarchical | dom_step_abort | 205 | 4% | 5% | 3% | 78% |
| timing | hierarchical | dom_step_replan | 205 | 31% | 35% | 21% | 67% |
| timing | hierarchical | none | 205 | 32% | 40% | 19% | 52% |
| timing | hierarchical | rebind_step | 205 | 27% | 55% | 37% | 73% |
| timing | hierarchical | dom_subtask_replan | 205 | 21% | 36% | 21% | 63% |
