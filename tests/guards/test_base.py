from stalehand.guards.base import PROCEED, Context, Guard


def test_default_guard_always_proceeds():
    g = Guard()
    ctx = Context(env=None, task="t", subtask="s", subtask_step=0, subtask_png=b"", step=3, png=b"")
    g.on_subtask(ctx)
    assert g.before_think(ctx) == PROCEED and g.before_act(ctx) == PROCEED
    assert g.name == "none" and g.planner_mode == "plain"
