from stalehand.agents.flat import Flat
from stalehand.guards.base import ABORT, PROCEED, REPLAN, Guard
from stalehand.scenarios.domains import inbox

from .fake_env import FakeEnv
from .test_hierarchical import CLICK, executor

SCEN = inbox.build(seed=0, kind="relative", index=0, variant="L1")


def test_executor_gets_the_whole_task_every_step():
    e = executor(CLICK, CLICK, "Action: finished(content='')")
    t = Flat(None, e, Guard(), max_steps=10).run(FakeEnv(commit_on_click="m01"), SCEN)
    assert t.architecture == "flat" and t.end_reason == "executor_done"
    assert all(SCEN.task in r.prompt for r in e.calls) and len(e.calls) == 3
    assert t.calls_by_role() == {"executor": 3}
    assert "1. Action: click" in e.calls[2].prompt


def test_step_limit():
    t = Flat(None, executor(*[CLICK] * 9), Guard(), max_steps=3).run(FakeEnv(), SCEN)
    assert t.end_reason == "max_steps" and t.calls_by_role() == {"executor": 3}


class Scripted(Guard):
    def __init__(self, act):
        self.act = list(act)

    def before_act(self, ctx):
        return self.act.pop(0) if self.act else PROCEED


def test_replan_before_acting_takes_a_fresh_look():
    env = FakeEnv()
    t = Flat(None, executor(CLICK, CLICK, "Action: finished(content='')"), Scripted([REPLAN]), max_steps=10).run(env, SCEN)
    assert len(env.actions) == 1 and t.end_reason == "executor_done"


def test_abort():
    t = Flat(None, executor(CLICK), Scripted([ABORT]), max_steps=10).run(FakeEnv(), SCEN)
    assert t.end_reason == "guard_abort"
