Built from 4305 scored episodes. Each table pairs episodes by scenario: same tasks, same guard, one thing changed. Difference is the arm's success rate minus the reference's, with a 95% bootstrap interval over scenario templates (10000 resamples, seed 0) and an exact McNemar test. The Holm column adjusts p over every comparison on the same axis.

## Architecture: `delegated` against `hierarchical`

| guard | timing | subset | pairs | hierarchical | delegated | difference | 95% CI | only delegated vs only hierarchical succeeded | McNemar | Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| dom_subtask_replan | after_handoff | all | 205 | 63% | 67% | +4 pts | [-1, +10] | 15 vs 6 | p = 0.078 | p = 1.000 |
| dom_subtask_replan | after_handoff | relevant | 55 | 58% | 69% | +11 pts | [+2, +21] | 7 vs 1 | p = 0.070 | p = 1.000 |
| dom_subtask_replan | after_handoff | harmless | 145 | 67% | 69% | +2 pts | [-3, +7] | 8 vs 5 | p = 0.581 | p = 1.000 |
| none | after_handoff | all | 205 | 50% | 53% | +3 pts | [+0, +7] | 11 vs 4 | p = 0.118 | p = 1.000 |
| none | after_handoff | relevant | 55 | 4% | 15% | +11 pts | [+4, +18] | 6 vs 0 | p = 0.031 | p = 0.594 |
| none | after_handoff | harmless | 145 | 69% | 70% | +1 pts | [-4, +6] | 5 vs 4 | p = 1.000 | p = 1.000 |
| rebind_dom | after_handoff | all | 205 | 62% | 63% | +0 pts | [-10, +9] | 21 vs 20 | p = 1.000 | p = 1.000 |
| rebind_dom | after_handoff | relevant | 55 | 55% | 67% | +13 pts | [+2, +24] | 10 vs 3 | p = 0.092 | p = 1.000 |
| rebind_dom | after_handoff | harmless | 145 | 68% | 63% | -4 pts | [-17, +8] | 11 vs 17 | p = 0.345 | p = 1.000 |
| replan_every_step | after_handoff | all | 205 | 76% | 75% | -0 pts | [-6, +5] | 10 vs 11 | p = 1.000 | p = 1.000 |
| replan_every_step | after_handoff | relevant | 55 | 80% | 75% | -5 pts | [-13, +2] | 1 vs 4 | p = 0.375 | p = 1.000 |
| replan_every_step | after_handoff | harmless | 145 | 77% | 78% | +1 pts | [-6, +8] | 9 vs 7 | p = 0.804 | p = 1.000 |

## Architecture: `flat` against `hierarchical`

| guard | timing | subset | pairs | hierarchical | flat | difference | 95% CI | only flat vs only hierarchical succeeded | McNemar | Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| none | after_handoff | all | 205 | 50% | 53% | +3 pts | [-6, +11] | 32 vs 26 | p = 0.512 | p = 1.000 |
| none | after_handoff | relevant | 55 | 4% | 33% | +29 pts | [+11, +45] | 18 vs 2 | p < 0.001 | p = 0.010 |
| none | after_handoff | harmless | 145 | 69% | 62% | -7 pts | [-19, +4] | 14 vs 24 | p = 0.143 | p = 1.000 |

## Architecture: `hierarchical_stall` against `hierarchical`

| guard | timing | subset | pairs | hierarchical | hierarchical_stall | difference | 95% CI | only hierarchical_stall vs only hierarchical succeeded | McNemar | Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| none | after_handoff | all | 205 | 50% | 58% | +8 pts | [+2, +15] | 18 vs 2 | p < 0.001 | p = 0.010 |
| none | after_handoff | relevant | 55 | 4% | 9% | +5 pts | [+0, +11] | 3 vs 0 | p = 0.250 | p = 1.000 |
| none | after_handoff | harmless | 145 | 69% | 78% | +9 pts | [+1, +19] | 15 vs 2 | p = 0.002 | p = 0.047 |
| rebind_dom | after_handoff | all | 205 | 62% | 74% | +11 pts | [+2, +20] | 32 vs 9 | p < 0.001 | p = 0.010 |
| rebind_dom | after_handoff | relevant | 55 | 55% | 75% | +20 pts | [+9, +31] | 11 vs 0 | p < 0.001 | p = 0.021 |
| rebind_dom | after_handoff | harmless | 145 | 68% | 76% | +8 pts | [-2, +19] | 21 vs 9 | p = 0.043 | p = 0.770 |
| replan_every_step | after_handoff | all | 205 | 76% | 80% | +4 pts | [-0, +10] | 13 vs 4 | p = 0.049 | p = 0.834 |
| replan_every_step | after_handoff | relevant | 55 | 80% | 84% | +4 pts | [-5, +15] | 4 vs 2 | p = 0.688 | p = 1.000 |
| replan_every_step | after_handoff | harmless | 145 | 77% | 81% | +5 pts | [-1, +11] | 9 vs 2 | p = 0.065 | p = 1.000 |

## Change timing: `mid_step` against `after_handoff`

| architecture | guard | subset | pairs | after_handoff | mid_step | difference | 95% CI | only mid_step vs only after_handoff succeeded | McNemar | Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| hierarchical | dom_subtask_replan | all | 205 | 63% | 42% | -21 pts | [-28, -14] | 4 vs 47 | p < 0.001 | p < 0.001 |
| hierarchical | dom_subtask_replan | relevant | 55 | 58% | 31% | -27 pts | [-43, -12] | 3 vs 18 | p = 0.001 | p = 0.006 |
| hierarchical | dom_subtask_replan | harmless | 145 | 67% | 48% | -19 pts | [-29, -10] | 1 vs 29 | p < 0.001 | p < 0.001 |
| hierarchical | none | all | 205 | 50% | 44% | -5 pts | [-11, -0] | 4 vs 15 | p = 0.019 | p = 0.038 |
| hierarchical | none | relevant | 55 | 4% | 5% | +2 pts | [-4, +8] | 2 vs 1 | p = 1.000 | p = 1.000 |
| hierarchical | none | harmless | 145 | 69% | 61% | -8 pts | [-15, -2] | 2 vs 14 | p = 0.004 | p = 0.013 |
| hierarchical | rebind_step | all | 205 | 59% | 38% | -20 pts | [-28, -13] | 6 vs 48 | p < 0.001 | p < 0.001 |
| hierarchical | rebind_step | relevant | 55 | 53% | 25% | -27 pts | [-39, -15] | 2 vs 17 | p < 0.001 | p = 0.004 |
| hierarchical | rebind_step | harmless | 145 | 63% | 44% | -19 pts | [-28, -9] | 4 vs 31 | p < 0.001 | p < 0.001 |
