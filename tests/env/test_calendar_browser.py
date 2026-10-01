import pytest

from stalehand.env.actions import Click
from stalehand.scenarios.domains import calendar

pytestmark = pytest.mark.browser


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def test_join_is_a_commit(env):
    s = calendar.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(centre(env.role_box("join")))
    assert env.commits()[-1]["itemId"] == s.stale_target


def test_added_meeting_shows_at_change_step(env):
    s = calendar.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
    env.reset(s)
    env.act(Click(5, 5))
    assert s.target_at(1) != s.stale_target and s.target_at(1) in env.item_boxes()


def test_reschedule_moves_target_below_the_other_meeting(env):
    s = calendar.build(seed=0, kind="relative", index=0, variant="reschedule", change_step=1)
    env.reset(s)
    env.act(Click(5, 5))
    boxes = env.item_boxes()
    assert boxes[s.stale_target][1] > boxes[s.target_at(1)][1]
