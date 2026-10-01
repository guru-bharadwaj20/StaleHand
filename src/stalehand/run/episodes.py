"""Run a job's scenarios one episode at a time, scoring each and appending it to results.jsonl.

A row in results.jsonl marks an episode as finished; its trajectory is written first. A rerun of the same job skips
finished scenarios, so a job that dies halfway (a reboot, a killed model server) resumes where it stopped.
"""
import json
import os
from pathlib import Path
from typing import Sequence

from ..metrics.outcome import score


class ResultLog:
    def __init__(self, out_dir):
        self.dir = Path(out_dir)
        self.path = self.dir / "results.jsonl"
        (self.dir / "trajectories").mkdir(parents=True, exist_ok=True)
        self.done = set()
        if self.path.exists():
            good = []
            for line in self.path.read_text().splitlines():
                try:
                    good.append(json.loads(line))
                except json.JSONDecodeError:
                    break  # a partial last line from a crash; the episode reruns
            self.path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in good))
            self.done = {r["scenario_id"] for r in good}

    def add(self, row: dict, trajectory) -> None:
        (self.dir / "trajectories" / f"{row['scenario_id']}.json").write_text(json.dumps(trajectory.to_dict()))
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.done.add(row["scenario_id"])


def run_episodes(job, scenarios: Sequence, agent, env, out_dir, log=print) -> int:
    """Run every scenario not already in out_dir/results.jsonl; return how many ran now."""
    results = ResultLog(out_dir)
    ran = 0
    for s in scenarios:
        if s.id in results.done:
            continue
        traj = agent.run(env, s)
        row = score(s, traj)
        row["run"] = {"job": job.id, "seed": job.seed, "planner": job.planner, "executor": job.executor}
        results.add(row, traj)
        ran += 1
        log(f"{len(results.done)}/{len(scenarios)} {s.id} {row['outcome']} ({row['end_reason']})")
    return ran
