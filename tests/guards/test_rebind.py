import pytest

from stalehand.agents.trajectory import Trajectory
from stalehand.guards.base import PROCEED, REBIND, REPLAN, Context
from stalehand.guards.rebind import Rebind
from stalehand.models.base import ScriptedVLM

EXTRA = {"rule": "the most recent email from Samuel Lee", "target": "Q3 budget review", "action": "open it"}


class Env:
    def __init__(self, external=0):
        self.external, self.marks = external, 0

    def mark_external(self):
        self.marks += 1
        self.external = 0

    def external_since_mark(self):
        return self.external


def ctx(step=2, env=None, png=b"new"):
    return Context(env=env or Env(), task="Open the latest email from Samuel Lee", subtask="open it - Q3 budget review",
                   subtask_step=0, subtask_png=b"old", step=step, png=png, extra=dict(EXTRA),
                   trajectory=Trajectory("s", "hierarchical", "rebind_step"))


def resolver(reply):
    return ScriptedVLM([("", reply)], name="checker")


def test_same_target_proceeds():
    m = resolver("Target: q3 Budget Review.")
    c = ctx()
    assert Rebind(m).before_think(c) == PROCEED
    assert c.subtask == "open it - Q3 budget review"
    assert "the most recent email from Samuel Lee" in m.calls[0].prompt and m.calls[0].image_png == b"new"
    assert c.trajectory.calls_by_role() == {"checker": 1}


def test_moved_target_rebinds_without_planner():
    c = ctx()
    assert Rebind(resolver("Target: Vendor contract renewal")).before_think(c) == REBIND
    assert c.subtask == "open it - Vendor contract renewal"
    assert c.extra["target"] == "Vendor contract renewal" and c.extra["rule"] == EXTRA["rule"]


def test_no_match_replans():
    assert Rebind(resolver("Target: NONE")).before_think(ctx()) == REPLAN


def test_unparsed_reply_proceeds():
    assert Rebind(resolver("I am not sure")).before_think(ctx()) == PROCEED


def test_no_check_on_the_planning_screen():
    m = resolver("Target: other")
    assert Rebind(m).before_think(ctx(step=0, png=b"old")) == PROCEED and m.calls == []


def test_checks_a_changed_screen_at_the_handoff_step():
    assert Rebind(resolver("Target: Vendor contract renewal")).before_think(ctx(step=0)) == REBIND


def test_dom_trigger_checks_only_after_external_changes():
    m = resolver("Target: Vendor contract renewal")
    g = Rebind(m, trigger="dom")
    env = Env()
    c = ctx(env=env)
    g.on_subtask(c)
    assert g.before_think(c) == PROCEED and m.calls == []
    env.external = 3
    assert g.before_think(c) == REBIND and len(m.calls) == 1
    assert env.external == 0  # re-marked, so the same change is not checked twice


def test_names_and_planner_mode():
    assert Rebind(resolver("x")).name == "rebind_step"
    assert Rebind(resolver("x"), trigger="dom").name == "rebind_dom"
    assert Rebind(resolver("x")).planner_mode == "bound"
    with pytest.raises(ValueError):
        Rebind(resolver("x"), trigger="sometimes")
