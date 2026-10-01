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


NAMES = {it.get("name"): it.id for it in list(SCEN.items) + [i for c in SCEN.changes for i in c.change.items]}


class NameFollower(ScriptedVLM):
    """Clicks whichever product its subtask names, then adds it to the cart."""
    def __init__(self, envs):
        super().__init__([], name="e")
        self.envs = envs

    def generate(self, requests):
        self.calls.extend(requests)
        env = self.envs[0]
        if env.step == 0:
            return ["Action: wait()"]
        if env.step == 1:
            name = next(n for n in NAMES if f"- {n}" in requests[0].prompt)
            return [click(env.item_boxes()[NAMES[name]])]
        if env.step == 2:
            return [click(env.role_box("add-to-cart"))]
        return ["Action: finished(content='')"]


def test_rebind_guard_follows_the_moved_target(tmp_path):
    write_jsonl([SCEN], tmp_path / "s.jsonl")
    stale_name = next(it.get("name") for it in SCEN.items if it.id == SCEN.stale_target)
    final_name = next(n for n, i in NAMES.items() if i == SCEN.target_at(1))
    planned = []

    class BoundPlanner(ScriptedVLM):
        def generate(self, requests):
            self.calls.extend(requests)
            out = []
            for r in requests:
                if r.prompt.startswith("Look at the current screenshot"):
                    out.append(f"Target: {final_name}")
                elif planned:
                    out.append("Target rule: DONE")
                else:
                    planned.append(1)
                    out.append(f"Target rule: the cheapest USB-C cable\nTarget: {stale_name}\n"
                               "Action: open it and add it to the cart")
            return out
    envs = []

    def make_env(timing):
        envs.append(BrowserEnv(change_timing=timing))
        return envs[0]
    job = Job("x", "e2e", "s.jsonl", "hierarchical", "rebind_step", "p", "e", 0, 8, "before_observation")
    load = lambda name, role: BoundPlanner([], name="p") if role == "planner" else NameFollower(envs)
    execute(job, tmp_path / "run", root=tmp_path, load_model=load, make_env=make_env, backend="scripted")
    row = json.loads((tmp_path / "run" / "results.jsonl").read_text())
    assert row["outcome"] == "success" and row["fired"] >= 1 and not row["false_alarm"]
    assert row["planner_calls"] == 2  # the first subtask and DONE: the rebind cost no planner call
