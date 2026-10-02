Built from 5669 episodes with a harmless change. Missed: the first item the agent opened was not the correct one. The last two columns are over the missed episodes only.

| run set | architecture | guard | episodes | first open missed | then succeeded | then committed to a wrong item |
|---|---|---|---|---|---|---|
| delegated | delegated | dom_subtask_replan | 145 | 13% | 0% | 100% |
| delegated | delegated | none | 145 | 13% | 0% | 100% |
| delegated | delegated | rebind_dom | 145 | 13% | 16% | 84% |
| delegated | delegated | replan_every_step | 145 | 12% | 0% | 100% |
| domains | hierarchical | dom_subtask_replan | 170 | 6% | 0% | 9% |
| domains | hierarchical | none | 170 | 9% | 0% | 19% |
| domains | hierarchical | replan_every_step | 170 | 8% | 0% | 7% |
| domains | hierarchical | rebind_step | 170 | 15% | 0% | 15% |
| domains | hierarchical | pixel_0.02_replan | 170 | 8% | 0% | 21% |
| domains | hierarchical | rebind_dom | 170 | 15% | 0% | 16% |
| domains | hierarchical | rule_subtask | 170 | 15% | 0% | 4% |
| domains | hierarchical | self_check | 170 | 9% | 0% | 19% |
| domains_lab | hierarchical | none | 69 | 12% | 0% | 0% |
| domains_lab | hierarchical | replan_every_step | 57 | 9% | 0% | 0% |
| domains_lab | hierarchical | rebind_dom | 53 | 6% | 0% | 67% |
| flat | flat | none | 145 | 74% | 53% | 31% |
| flat_internvl | flat | none | 145 | 66% | 1% | 72% |
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
| small_planner | hierarchical | rebind_dom | 145 | 48% | 10% | 74% |
| small_planner | hierarchical | none | 145 | 12% | 0% | 72% |
| small_planner | hierarchical | replan_every_step | 145 | 16% | 0% | 87% |
| small_planner | hierarchical | dom_subtask_replan | 145 | 16% | 0% | 61% |
| timing | hierarchical | dom_step_abort | 145 | 3% | 0% | 75% |
| timing | hierarchical | dom_step_replan | 145 | 10% | 0% | 57% |
| timing | hierarchical | none | 145 | 72% | 53% | 14% |
| timing | hierarchical | rebind_step | 145 | 72% | 30% | 40% |
| timing | hierarchical | dom_subtask_replan | 145 | 72% | 35% | 42% |
