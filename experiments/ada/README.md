# Matrices for the RTX 4500 Ada

The Ada cannot hold Qwen3-VL-8B and an executor side by side, even in fp8 (see `docs/progress.md`). These
matrices fit the card as it is. All of them use the main comparison's scenarios and timing (`experiments/main/`),
so their rows pair with the lab results scenario by scenario.

| Matrix | On the card | What it answers |
|---|---|---|
| `flat_internvl.json` | InternVL3.5-8B alone (bf16) | Does the second family follow the UI-TARS action format? Parse failures and success with no change are the gate before any hierarchical second-family run. |
| `flat_uitars_fp8.json` | UI-TARS-1.5-7B alone, fp8 | Precision control: the lab runs the same matrix (`experiments/main/matrix_flat.json`) in bf16, so the paired difference is the cost of fp8. |
| `small_planner_fp8.json` | Qwen3-VL-4B planner and UI-TARS-1.5-7B executor, both fp8 | Does a smaller planner change how often subtasks go stale, and do the guards still help? |

Serve with `scripts/ada/`, set `STALEHAND_PRECISION=fp8` (or `bf16`) in the host's `env` in `runner/hosts.json`
so `config.json` records it, and write results to `results/guru-4500/`.
