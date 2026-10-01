import pytest

from stalehand.scenarios.domains import inbox
from stalehand.scenarios.serialize import scenario_to_dict

VARIANTS = ("none", "cosmetic", "L0", "L1", "L3")


def test_same_arguments_give_same_scenario():
    a = inbox.build(seed=0, kind="relative", index=4, variant="L1")
    b = inbox.build(seed=0, kind="relative", index=4, variant="L1")
    assert scenario_to_dict(a) == scenario_to_dict(b)


def test_different_seeds_give_different_inboxes():
    a = inbox.build(seed=0, kind="relative", index=4, variant="L1")
    b = inbox.build(seed=1, kind="relative", index=4, variant="L1")
    assert a.items != b.items


def test_variants_share_the_first_screen():
    firsts = {v: inbox.build(seed=0, kind="fixed", index=2, variant=v).items for v in VARIANTS}
    assert all(items == firsts["none"] for items in firsts.values())


def test_first_screen_has_ten_rows_newest_first():
    s = inbox.build(seed=0, kind="relative", index=0, variant="none")
    received = [it.get("received") for it in s.items]
    assert len(received) == 10 and received == sorted(received, reverse=True)


@pytest.mark.parametrize("variant,kind,expected", [
    ("L1", "relative", "relevant"), ("L3", "relative", "relevant"), ("L0", "relative", "irrelevant"),
    ("L1", "fixed", "irrelevant"), ("L3", "fixed", "irrelevant"), ("L0", "fixed", "irrelevant"),
    ("none", "relative", "none"), ("cosmetic", "fixed", "none")])
def test_change_kind_follows_variant(variant, kind, expected):
    for index in range(20):
        assert inbox.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


def test_relative_target_is_not_the_top_row():
    for index in range(20):
        s = inbox.build(seed=0, kind="relative", index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_relative_first_screen_has_two_mails_from_sender():
    s = inbox.build(seed=0, kind="relative", index=0, variant="none")
    sender = dict(s.criterion.filters)["sender"]
    assert sum(it.get("sender") == sender for it in s.items) == 2


def test_task_text_names_sender_and_fixed_topic():
    s = inbox.build(seed=0, kind="fixed", index=0, variant="L1")
    f = dict(s.criterion.filters)
    assert f["sender"] in s.task and f["topic"] in s.task


def test_arrivals_happen_at_change_step():
    s = inbox.build(seed=0, kind="relative", index=0, variant="L3", change_step=2)
    assert s.target_at(1) == s.stale_target and s.target_at(2) != s.stale_target


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError):
        inbox.build(seed=0, kind="relative", index=0, variant="L7")
