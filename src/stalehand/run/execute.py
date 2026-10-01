"""Turn a job into a run: load its models, build its guard and agent, open the environment, run the episodes."""
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from ..agents.delegated import Delegated
from ..agents.flat import Flat
from ..agents.hierarchical import Hierarchical
from ..guards import registry as guards
from ..models.registry import MODELS
from ..scenarios.export import read_jsonl
from .episodes import run_episodes
from .provenance import config, git_state, model_info

ARCHITECTURES = {"hierarchical": Hierarchical, "delegated": Delegated, "flat": Flat}
PLANNERLESS = ("flat",)  # these jobs name their planner "none"


def _resuming(out: Path, job, root: Path) -> bool:
    """True if out already holds this job run by the same code; an error if it holds another job or other code."""
    path = out / "config.json"
    if not path.exists():
        return False
    old = json.loads(path.read_text())
    if old["job"] != asdict(job):
        raise ValueError(f"{out} holds a different job ({old['job']['id']}); refusing to mix results")
    if old["git"] != git_state(root):
        raise ValueError(f"{out} was run by different code ({old['git']}); move it aside to rerun")
    return True


def execute(job, out_dir, root, load_model: Callable[[str, str], object], make_env: Callable[[str], object],
            backend: str, log=print) -> int:
    """Run the job's unfinished episodes into out_dir; return how many ran."""
    if job.architecture not in ARCHITECTURES:
        raise ValueError(f"unknown architecture {job.architecture!r}; available: {sorted(ARCHITECTURES)}")
    root, out = Path(root), Path(out_dir)
    resuming = _resuming(out, job, root)
    scenarios = read_jsonl(root / job.scenarios)
    random.seed(job.seed)
    planner = None if job.architecture in PLANNERLESS else load_model(job.planner, "planner")
    executor = load_model(job.executor, "executor")
    if not resuming:
        out.mkdir(parents=True, exist_ok=True)
        cfg = config(job, {"planner": None if planner is None else model_info(job.planner, planner, backend),
                           "executor": model_info(job.executor, executor, backend)}, root)
        (out / "config.json").write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    guard = guards.make(job.guard, checker=planner)
    coords = MODELS[job.executor].coords if job.executor in MODELS else "abs"
    agent = ARCHITECTURES[job.architecture](planner, executor, guard, max_steps=job.max_steps, executor_coords=coords)
    env = make_env(job.change_timing)
    try:
        return run_episodes(job, scenarios, agent, env, out, log=log)
    finally:
        env.close()
