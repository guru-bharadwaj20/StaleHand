import pytest

from stalehand.env.actions import Click, Type
from stalehand.scenarios.domains import inbox, shop

pytestmark = pytest.mark.browser


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def test_reset_returns_png_screenshot(env):
    obs = env.reset(inbox.build(seed=0, kind="relative", index=0, variant="L1"))
    assert obs.step == 0 and obs.png[:8] == b"\x89PNG\r\n\x1a\n"


def test_item_boxes_cover_visible_rows(env):
    s = inbox.build(seed=0, kind="relative", index=0, variant="L1")
    env.reset(s)
    boxes = env.item_boxes()
    assert set(boxes) == {it.id for it in s.items}
    assert all(w > 0 and h > 0 for _, _, w, h in boxes.values())


def test_change_applies_when_its_step_starts(env):
    s = inbox.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
    env.reset(s)
    assert s.target_at(1) not in env.item_boxes()
    obs = env.act(Click(5, 5))
    assert obs.step == 1 and s.target_at(1) in env.item_boxes()


def test_clicking_a_row_opens_it(env):
    s = inbox.build(seed=0, kind="fixed", index=0, variant="none")
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    assert env.events()[-1] == {**env.events()[-1], "kind": "open", "itemId": s.stale_target}


def test_typing_reaches_focused_input(env):
    s = inbox.build(seed=0, kind="fixed", index=0, variant="none")
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(centre(env.role_box("forward")))
    env.act(centre(env.role_box("to")))
    env.act(Type("laura@example.com"))
    assert env.view()["name"] == "compose" and env.view()["to"] == "laura@example.com"


def test_shop_add_to_cart_is_a_commit(env):
    s = shop.build(seed=0, kind="cheapest", index=0, variant="none")
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(centre(env.role_box("add-to-cart")))
    assert env.commits()[-1]["itemId"] == s.stale_target


def test_mutations_counted_since_mark(env):
    s = inbox.build(seed=0, kind="relative", index=0, variant="L0", change_step=1)
    env.reset(s)
    env.mark_mutations()
    assert env.mutations_since_mark() == 0
    env.act(Click(5, 5))  # irrelevant arrivals land at step 1
    assert env.mutations_since_mark() > 0


def test_cosmetic_change_also_mutates_dom(env):
    s = inbox.build(seed=0, kind="relative", index=0, variant="cosmetic", change_step=1)
    env.reset(s)
    env.mark_mutations()
    env.act(Click(5, 5))
    assert env.mutations_since_mark() > 0


def test_own_actions_are_not_external_changes(env):
    s = inbox.build(seed=0, kind="fixed", index=0, variant="none")
    env.reset(s)
    env.mark_external()
    env.act(centre(env.item_boxes()[s.stale_target]))  # opening a mail rebuilds the DOM
    assert env.mutations_since_mark() > 0 and env.external_since_mark() == 0


def test_scheduled_change_counts_as_external(env):
    s = inbox.build(seed=0, kind="fixed", index=0, variant="L0", change_step=2)
    env.reset(s)
    env.mark_external()
    env.act(Click(5, 5))
    assert env.external_since_mark() == 0
    env.act(Click(5, 5))
    assert env.external_since_mark() > 0


def test_mid_step_change_lands_after_the_screenshot():
    from stalehand.env.browser import BrowserEnv
    e = BrowserEnv(change_timing="mid_step")
    try:
        s = inbox.build(seed=0, kind="relative", index=0, variant="L1", change_step=1)
        e.reset(s)
        obs = e.act(Click(5, 5))  # step 1 begins; the change has not landed yet
        assert obs.step == 1 and s.target_at(1) not in e.item_boxes()
        e.begin_action()  # the executor is about to act: the page changes under it
        assert s.target_at(1) in e.item_boxes()
    finally:
        e.close()


def test_unknown_change_timing_is_rejected():
    from stalehand.env.browser import BrowserEnv
    with pytest.raises(ValueError):
        BrowserEnv(change_timing="whenever")
