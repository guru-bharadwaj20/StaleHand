from stalehand.guards.base import PROCEED, REPLAN, Context
from stalehand.guards.replan import ReplanEveryStep


def ctx(step, subtask_step):
    return Context(env=None, task="t", subtask="s", subtask_step=subtask_step, subtask_png=b"", step=step, png=b"")


def test_fresh_subtask_proceeds():
    assert ReplanEveryStep().before_think(ctx(3, 3)) == PROCEED


def test_older_subtask_is_replanned():
    assert ReplanEveryStep().before_think(ctx(4, 3)) == REPLAN


def test_replans_when_the_screen_changed_at_the_handoff_step():
    from stalehand.guards.base import Context
    c = Context(env=None, task="t", subtask="s", subtask_step=0, subtask_png=b"planner", step=0, png=b"changed")
    assert ReplanEveryStep().before_think(c) == REPLAN
