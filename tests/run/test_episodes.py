import json
from pathlib import Path

import jsonschema

from stalehand.agents.trajectory import Trajectory
from stalehand.run.episodes import ResultLog, run_episodes
from stalehand.run.job import Job
from stalehand.scenarios.domains import shop

SCHEMA = json.loads((Path(__file__).parents[2] / "schema" / "result.schema.json").read_text())
JOB = Job("35eb0fb0bcee", "pilot", "s.jsonl", "hierarchical", "none", "p", "e", 7, 12)
SCEN = [shop.build(seed=0, kind="cheapest", index=i, variant="L1") for i in range(3)]


class CommitStale:
    """Agent stand-in: commits on the stale target and records which scenarios it ran."""
    def __init__(self, fail_on=None):
        self.ran, self.fail_on = [], fail_on

    def run(self, env, scenario):
        if scenario.id == self.fail_on:
            raise RuntimeError("model server went away")
        self.ran.append(scenario.id)
        t = Trajectory(scenario.id, "hierarchical", "none")
        t.finish("planner_done", [{"kind": "add_to_cart", "itemId": scenario.stale_target, "commit": True,
                                   "step": 2}])
        return t


def rows(out):
    return [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]


def test_writes_one_scored_row_and_trajectory_per_scenario(tmp_path):
    n = run_episodes(JOB, SCEN, CommitStale(), env=None, out_dir=tmp_path)
    assert n == 3
    r = rows(tmp_path)
    assert [x["scenario_id"] for x in r] == [s.id for s in SCEN]
    assert {x["outcome"] for x in r} == {"stale"}
    for x in r:
        jsonschema.validate(x, SCHEMA)
    assert r[0]["run"] == {"job": "35eb0fb0bcee", "seed": 7, "planner": "p", "executor": "e"}
    saved = json.loads((tmp_path / "trajectories" / f"{SCEN[0].id}.json").read_text())
    assert saved["end_reason"] == "planner_done"


def test_resume_skips_finished_scenarios(tmp_path):
    first = CommitStale(fail_on=SCEN[1].id)
    try:
        run_episodes(JOB, SCEN, first, env=None, out_dir=tmp_path)
    except RuntimeError:
        pass
    assert first.ran == [SCEN[0].id]
    second = CommitStale()
    assert run_episodes(JOB, SCEN, second, env=None, out_dir=tmp_path) == 2
    assert second.ran == [SCEN[1].id, SCEN[2].id]
    assert [x["scenario_id"] for x in rows(tmp_path)] == [s.id for s in SCEN]


def test_truncated_last_row_is_dropped_and_rerun(tmp_path):
    run_episodes(JOB, SCEN[:2], CommitStale(), env=None, out_dir=tmp_path)
    path = tmp_path / "results.jsonl"
    text = path.read_text()
    path.write_text(text[: text.rindex("{") + 10])  # a crash mid-write
    log = ResultLog(tmp_path)
    assert log.done == {SCEN[0].id}
    assert path.read_text().count("\n") == 1
