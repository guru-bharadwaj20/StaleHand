from stalehand.agents.trajectory import Trajectory
from stalehand.guards.base import PROCEED, REPLAN, Context
from stalehand.guards.self_check import SelfCheck
from stalehand.models.base import ScriptedVLM


def ctx(step=2, subtask_step=0):
    return Context(env=None, task="Forward the latest email from Sam", subtask="open the Budget email",
                   subtask_step=subtask_step, subtask_png=b"old", step=step, png=b"new",
                   trajectory=Trajectory("s", "hierarchical", "self_check"))


def test_stale_verdict_replans_and_is_recorded():
    m = ScriptedVLM([("", "Verdict: STALE\nReason: newer mail")], name="checker")
    c = ctx()
    assert SelfCheck(m).before_think(c) == REPLAN
    assert c.trajectory.calls_by_role() == {"checker": 1}
    assert m.calls[0].image_png == b"new" and "open the Budget email" in m.calls[0].prompt


def test_valid_or_unparsed_verdict_proceeds():
    assert SelfCheck(ScriptedVLM([("", "Verdict: VALID")])).before_think(ctx()) == PROCEED
    assert SelfCheck(ScriptedVLM([("", "hmm")])).before_think(ctx()) == PROCEED


def test_no_check_on_the_screen_the_subtask_was_written_on():
    m = ScriptedVLM([("", "Verdict: STALE")])
    assert SelfCheck(m).before_think(ctx(step=0, subtask_step=0)) == PROCEED and m.calls == []
