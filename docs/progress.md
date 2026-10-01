# Progress

Runs that failed, were skipped or are blocked are recorded here rather than dropped (see `CONTRIBUTING.md`).

## Blocked

- **Second-family experiments (`results/guru-4500/`)**, 2026-10-01. Not run: the main matrices they rerun do not
  exist yet, and `stalehand run-job` (the entry point the runner calls) is still open. Ready on Guru's side:
  `internvl3.5-8b` in the model registry and `scripts/ada/` to serve it next to the planner. Unblocks once
  `run-job` lands and the main inbox and shop comparison has a config to rerun.
