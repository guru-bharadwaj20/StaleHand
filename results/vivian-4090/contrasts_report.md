Built from 2665 scored episodes. Each table pairs episodes by scenario: same tasks, same guard, one thing changed. Difference is the arm's success rate minus the reference's, with a 95% bootstrap interval over scenario templates (10000 resamples, seed 0) and an exact McNemar test. The Holm column adjusts p over every comparison on the same axis.

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
