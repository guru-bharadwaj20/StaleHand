Mean tokens per episode, recounted from the logged replies (output) and the screenshot sent with every call (image). Prompt text was not logged and is not counted.

| run set | architecture | guard | episodes | planner output | executor output | checker output | image input |
|---|---|---|---|---|---|---|---|
| main | hierarchical | replan_every_step | 205 | 151 | 465 | 0 | 14,130 |
| main | hierarchical | rebind_step | 205 | 56 | 768 | 59 | 20,939 |
| main | hierarchical | pixel_0.02_replan | 205 | 102 | 562 | 0 | 13,288 |
| main | hierarchical | rebind_dom | 205 | 48 | 784 | 8 | 13,732 |
| main | hierarchical | self_check | 205 | 47 | 581 | 241 | 16,851 |
| main | hierarchical | rule_subtask | 205 | 43 | 824 | 0 | 13,202 |
| main | hierarchical | none | 205 | 39 | 608 | 0 | 10,916 |
| main | hierarchical | dom_subtask_replan | 205 | 57 | 617 | 0 | 11,765 |
