# Progress

Runs that failed, were skipped or are blocked are recorded here rather than dropped (see `CONTRIBUTING.md`).

## Blocked

- **Second-family experiments (`results/guru-4500/`)**, 2026-10-01. Not run: the main matrices they rerun do not
  exist yet, and `stalehand run-job` (the entry point the runner calls) is still open. Ready on Guru's side:
  `internvl3.5-8b` in the model registry and `scripts/ada/` to serve it next to the planner. Unblocks once
  `run-job` lands and the main inbox and shop comparison has a config to rerun.
  Checked on the Ada on 2026-10-01: `scripts/ada/setup.sh` installs vLLM 0.30.0 with CUDA available, and
  `scripts/ada/download.sh` fetched Qwen/Qwen3-VL-8B-Instruct at 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b and
  OpenGVLab/InternVL3_5-8B at 9bb6a56ad9cc69db95e2d4eeb15a52bbcac4ef79. Serving was not started: another
  project's vLLM server held 22.9 of 24.5 GB on the card and was left running.
