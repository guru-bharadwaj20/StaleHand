import json
from dataclasses import replace

import pytest

from stalehand.models.base import ScriptedVLM
from stalehand.run.execute import execute
from stalehand.run.job import Job
from stalehand.scenarios.domains import inbox
from stalehand.scenarios.export import write_jsonl

from ..agents.fake_env import FakeEnv

SCEN = [inbox.build(seed=0, kind="relative", index=i, variant="L1") for i in range(2)]
JOB = Job("x", "pilot", "s.jsonl", "hierarchical", "none", "planner-m", "executor-m", 3, 6, "before_observation")


def models(loaded):
    def load(name, role):
        loaded.append((name, role))
        if role == "planner":
            return ScriptedVLM([("", "Subtask: DONE")], name=name)
        return ScriptedVLM([("", "Action: finished(content='')")], name=name)
    return load


@pytest.fixture
def root(tmp_path):
    write_jsonl(SCEN, tmp_path / "s.jsonl")
    return tmp_path


def test_runs_every_scenario_and_writes_config(root):
    loaded, envs = [], []

    def make_env(timing):
        envs.append(timing)
        return FakeEnv()
    out = root / "runs" / "x"
    assert execute(JOB, out, root=root, load_model=models(loaded), make_env=make_env, backend="scripted") == 2
    assert loaded == [("planner-m", "planner"), ("executor-m", "executor")]
    assert envs == ["before_observation"]
    cfg = json.loads((out / "config.json").read_text())
    assert cfg["seed"] == 3 and cfg["job"]["guard"] == "none"
    assert cfg["models"]["planner"] == {"name": "planner-m", "id": "planner-m", "revision": None, "backend": "scripted"}
    rows = (out / "results.jsonl").read_text().splitlines()
    assert len(rows) == 2 and json.loads(rows[0])["outcome"] == "no_commit"


def test_rerun_keeps_config_and_runs_nothing(root):
    out = root / "runs" / "x"
    execute(JOB, out, root=root, load_model=models([]), make_env=lambda t: FakeEnv(), backend="scripted")
    before = (out / "config.json").read_text()
    assert execute(JOB, out, root=root, load_model=models([]), make_env=lambda t: FakeEnv(), backend="scripted") == 0
    assert (out / "config.json").read_text() == before


def test_refuses_directory_of_a_different_job(root):
    out = root / "runs" / "x"
    execute(JOB, out, root=root, load_model=models([]), make_env=lambda t: FakeEnv(), backend="scripted")
    with pytest.raises(ValueError, match="different job"):
        execute(replace(JOB, seed=4), out, root=root, load_model=models([]), make_env=lambda t: FakeEnv(),
                backend="scripted")


def test_self_check_guard_gets_a_checker(root):
    out = root / "runs" / "y"
    job = replace(JOB, guard="self_check")
    assert execute(job, out, root=root, load_model=models([]), make_env=lambda t: FakeEnv(), backend="scripted") == 2


def test_unknown_architecture_is_an_error(root):
    with pytest.raises(ValueError, match="architecture"):
        execute(replace(JOB, architecture="swarm"), root / "z", root=root, load_model=models([]),
                make_env=lambda t: FakeEnv(), backend="scripted")


def test_env_is_closed_even_when_an_episode_fails(root):
    class Boom(FakeEnv):
        closed = False

        def reset(self, scenario):
            raise RuntimeError("chrome died")

        def close(self):
            Boom.closed = True
    with pytest.raises(RuntimeError):
        execute(JOB, root / "w", root=root, load_model=models([]), make_env=lambda t: Boom(), backend="scripted")
    assert Boom.closed


def test_delegated_architecture(root):
    out = root / "runs" / "d"
    execute(replace(JOB, architecture="delegated"), out, root=root, load_model=models([]),
            make_env=lambda t: FakeEnv(), backend="scripted")
    row = json.loads((out / "results.jsonl").read_text().splitlines()[0])
    assert row["architecture"] == "delegated"
