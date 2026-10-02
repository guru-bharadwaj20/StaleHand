Mean tokens per episode, recounted from the logged replies (output) and the screenshot sent with every call (image). Prompt text was not logged and is not counted.

| run set | architecture | guard | episodes | planner output | executor output | checker output | image input |
|---|---|---|---|---|---|---|---|
| delegated | delegated | dom_subtask_replan | 205 | 63 | 580 | 0 | 11,600 |
| delegated | delegated | none | 205 | 45 | 575 | 0 | 10,753 |
| delegated | delegated | rebind_dom | 205 | 58 | 672 | 8 | 12,574 |
| delegated | delegated | replan_every_step | 205 | 148 | 464 | 0 | 14,108 |
| domains_lab | hierarchical | none | 97 | 34 | 941 | 0 | 14,774 |
| domains_lab | hierarchical | replan_every_step | 87 | 233 | 733 | 0 | 20,358 |
| domains_lab | hierarchical | rebind_dom | 70 | 46 | 744 | 5 | 13,474 |
| main | hierarchical | replan_every_step | 205 | 151 | 465 | 0 | 14,130 |
| main | hierarchical | rebind_step | 205 | 56 | 768 | 59 | 20,939 |
| main | hierarchical | pixel_0.02_replan | 205 | 102 | 562 | 0 | 13,288 |
| main | hierarchical | rebind_dom | 205 | 48 | 784 | 8 | 13,732 |
| main | hierarchical | self_check | 205 | 47 | 581 | 241 | 16,851 |
| main | hierarchical | rule_subtask | 205 | 43 | 824 | 0 | 13,202 |
| main | hierarchical | none | 205 | 39 | 608 | 0 | 10,916 |
| main | hierarchical | dom_subtask_replan | 205 | 57 | 617 | 0 | 11,765 |
| main_stall | hierarchical_stall | rebind_dom | 205 | 89 | 584 | 8 | 12,440 |
| main_stall | hierarchical_stall | replan_every_step | 205 | 149 | 467 | 0 | 14,215 |
| main_stall | hierarchical_stall | none | 205 | 52 | 523 | 0 | 10,532 |
| timing | hierarchical | dom_step_abort | 205 | 25 | 160 | 0 | 3,562 |
| timing | hierarchical | dom_step_replan | 205 | 57 | 682 | 0 | 12,809 |
| timing | hierarchical | none | 205 | 37 | 689 | 0 | 11,976 |
| timing | hierarchical | rebind_step | 205 | 81 | 816 | 57 | 21,574 |
| timing | hierarchical | dom_subtask_replan | 205 | 59 | 627 | 0 | 12,384 |
