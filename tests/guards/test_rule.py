from stalehand.guards.base import PROCEED, Context
from stalehand.guards.rule import RuleSubtask


def test_rule_guard_only_switches_planner_mode():
    g = RuleSubtask()
    c = Context(env=None, task="t", subtask="s", subtask_step=0, subtask_png=b"", step=5, png=b"")
    assert g.planner_mode == "rule" and g.before_think(c) == PROCEED and g.before_act(c) == PROCEED
