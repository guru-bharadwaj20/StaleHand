Built from 3439 episodes with a harmless change. Missed: the first item the agent opened was not the correct one. The last two columns are over the missed episodes only.

| run set | architecture | guard | episodes | first open missed | then succeeded | then committed to a wrong item |
|---|---|---|---|---|---|---|
| delegated | delegated | dom_subtask_replan | 145 | 13% | 0% | 100% |
| delegated | delegated | none | 145 | 13% | 0% | 100% |
| delegated | delegated | rebind_dom | 145 | 13% | 16% | 84% |
| delegated | delegated | replan_every_step | 145 | 12% | 0% | 100% |
| domains_lab | hierarchical | none | 69 | 12% | 0% | 0% |
| domains_lab | hierarchical | replan_every_step | 57 | 9% | 0% | 0% |
| domains_lab | hierarchical | rebind_dom | 53 | 6% | 0% | 67% |
| main | hierarchical | replan_every_step | 145 | 10% | 0% | 100% |
| main | hierarchical | rebind_step | 145 | 14% | 5% | 71% |
| main | hierarchical | pixel_0.02_replan | 145 | 10% | 0% | 100% |
| main | hierarchical | rebind_dom | 145 | 12% | 6% | 61% |
| main | hierarchical | self_check | 145 | 10% | 0% | 47% |
| main | hierarchical | rule_subtask | 145 | 28% | 7% | 56% |
| main | hierarchical | none | 145 | 10% | 0% | 57% |
| main | hierarchical | dom_subtask_replan | 145 | 11% | 0% | 81% |
| main_stall | hierarchical_stall | rebind_dom | 145 | 12% | 11% | 89% |
| main_stall | hierarchical_stall | replan_every_step | 145 | 10% | 0% | 100% |
| main_stall | hierarchical_stall | none | 145 | 10% | 0% | 79% |
| pilot | hierarchical | replan_every_step | 145 | 12% | 0% | 94% |
| pilot | hierarchical | none | 145 | 10% | 0% | 13% |
| pilot_shop_rerun | hierarchical | replan_every_step | 35 | 40% | 0% | 100% |
| pilot_shop_rerun | hierarchical | none | 35 | 40% | 0% | 64% |
| timing | hierarchical | dom_step_abort | 145 | 3% | 0% | 75% |
| timing | hierarchical | dom_step_replan | 145 | 10% | 0% | 57% |
| timing | hierarchical | none | 145 | 72% | 53% | 14% |
| timing | hierarchical | rebind_step | 145 | 72% | 30% | 40% |
| timing | hierarchical | dom_subtask_replan | 145 | 72% | 35% | 42% |
