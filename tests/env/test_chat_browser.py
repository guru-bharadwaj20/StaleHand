import pytest

from stalehand.env.actions import Click, Type
from stalehand.scenarios.domains import chat

pytestmark = pytest.mark.browser


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def test_item_boxes_cover_every_message(env):
    s = chat.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    boxes = env.item_boxes()
    assert set(boxes) == {it.id for it in s.items} and all(b[2] > 0 for b in boxes.values())


def test_reply_is_a_commit_in_reply_mode(env):
    s = chat.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(centre(env.role_box("body")))
    env.act(Type("Thanks!"))
    env.act(centre(env.role_box("send")))
    commit = env.commits()[-1]
    assert commit["itemId"] == s.stale_target and commit["detail"]["mode"] == "reply"


def test_new_message_shows_at_change_step(env):
    s = chat.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
    env.reset(s)
    env.act(Click(5, 5))
    assert s.target_at(1) != s.stale_target and s.target_at(1) in env.item_boxes()
