"""run-job's wiring against the real browser: an executor that follows the planner's stale target scores stale."""
import json

import pytest

from stalehand.env.browser import BrowserEnv
from stalehand.models.base import ScriptedVLM
from stalehand.run.execute import execute
from stalehand.run.job import Job
from stalehand.scenarios.domains import shop
from stalehand.scenarios.export import write_jsonl

pytestmark = pytest.mark.browser

SCEN = shop.build(seed=0, kind="cheapest", index=0, variant="L1", change_step=1)
JOB = Job("x", "e2e", "s.jsonl", "hierarchical", "none", "p", "e", 0, 8, "before_observation")


def click(box):
    x, y, w, h = box
    return f"Action: click(start_box='({int(x + w / 2)},{int(y + h / 2)})')"


class StaleFollower(ScriptedVLM):
    """Waits for the change, then opens the target the planner saw and adds it to the cart (positions read live)."""
    def __init__(self, envs):
        super().__init__([], name="e")
        self.envs = envs

    def generate(self, requests):
        env = self.envs[0]
        if env.step == 0:
            return ["Action: wait()"]
        if env.step == 1:
            return [click(env.item_boxes()[SCEN.stale_target])]
        if env.step == 2:
            return [click(env.role_box("add-to-cart"))]
        return ["Action: finished(content='')"]


class OneSubtask(ScriptedVLM):
    def generate(self, requests):
        self.calls.extend(requests)
        return ["Subtask: DONE" if len(self.calls) > 1 else "Subtask: add the cheapest item to the cart"]


def test_stale_follower_scores_stale(tmp_path):
    write_jsonl([SCEN], tmp_path / "s.jsonl")
    envs = []

    def make_env(timing):
        envs.append(BrowserEnv(change_timing=timing))
        return envs[0]

    def load(name, role):
        return OneSubtask([], name="p") if role == "planner" else StaleFollower(envs)
    out = tmp_path / "run"
    assert execute(JOB, out, root=tmp_path, load_model=load, make_env=make_env, backend="scripted") == 1
    row = json.loads((out / "results.jsonl").read_text())
    assert row["outcome"] == "stale" and row["commit_step"] >= 1
