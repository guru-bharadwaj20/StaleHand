import pytest

from stalehand.env.actions import Click, Type
from stalehand.scenarios.domains import files

pytestmark = pytest.mark.browser


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def share(env, item_id, to):
    env.act(centre(env.item_boxes()[item_id]))
    env.act(centre(env.role_box("share")))
    env.act(centre(env.role_box("to")))
    env.act(Type(to))
    env.act(centre(env.role_box("send")))


def test_item_boxes_cover_visible_rows(env):
    s = files.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    assert set(env.item_boxes()) == {it.id for it in s.items}


def test_share_is_a_commit_with_recipient(env):
    s = files.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    share(env, s.stale_target, s.meta["recipient"])
    commit = env.commits()[-1]
    assert commit["itemId"] == s.stale_target and commit["detail"]["to"] == s.meta["recipient"]


def test_upload_lands_at_change_step(env):
    s = files.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
    env.reset(s)
    assert s.target_at(1) not in env.item_boxes()
    env.act(Click(5, 5))
    assert s.target_at(1) in env.item_boxes()


def test_stale_share_after_upload_hits_old_file(env):
    s = files.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
    env.reset(s)
    share(env, s.stale_target, s.meta["recipient"])
    assert env.commits()[-1]["itemId"] == s.stale_target != s.target_at(1)


def test_rename_shows_new_name_on_open_file(env):
    s = files.build(seed=0, kind="fixed", index=0, variant="rename", change_step=2)
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(Click(5, 5))  # step 2: the open file is renamed
    assert env.view() == {"name": "details", "id": s.stale_target}
    renamed = next(it for it in s.items_at(2) if it.id == s.stale_target).get("name")
    assert "(final)" in renamed
