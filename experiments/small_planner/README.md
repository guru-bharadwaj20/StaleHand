# Small-planner arm

Qwen3-VL-4B as planner, UI-TARS-1.5-7B as executor, both in bf16 on the lab 4090s, under four guards. Same
scenarios and timing as the main comparison (`experiments/main/`), so rows pair with it scenario by scenario. The
question: does a weaker planner change how often subtasks go stale, and do the guards still help?
