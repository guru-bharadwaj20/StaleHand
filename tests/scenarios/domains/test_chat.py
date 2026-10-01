import pytest

from stalehand.scenarios.domains import chat
from stalehand.scenarios.serialize import scenario_to_dict

KINDS = ("fixed", "relative")


def test_same_arguments_give_same_scenario():
    a, b = (chat.build(seed=0, kind="relative", index=3, variant="L1") for _ in range(2))
    assert scenario_to_dict(a) == scenario_to_dict(b)


@pytest.mark.parametrize("kind", KINDS)
def test_variants_share_the_first_screen(kind):
    firsts = [chat.build(seed=0, kind=kind, index=1, variant=v).items for v in chat.VARIANTS]
    assert all(f == firsts[0] for f in firsts)


def test_arrivals_are_newer_than_the_first_screen():
    s = chat.build(seed=0, kind="relative", index=0, variant="L3")
    newest = max(it.get("sent") for it in s.items)
    assert all(it.get("sent") > newest for it in s.changes[0].change.items)


@pytest.mark.parametrize("kind,variant,expected", [
    ("relative", "L1", "relevant"), ("relative", "L3", "relevant"), ("relative", "L0", "irrelevant"),
    ("fixed", "L1", "irrelevant"), ("fixed", "L3", "irrelevant"), ("relative", "edited", "irrelevant"),
    ("fixed", "edited", "target_removed"), ("relative", "none", "none"), ("fixed", "cosmetic", "none")])
def test_change_kind_follows_variant(kind, variant, expected):
    for index in range(20):
        assert chat.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


def test_relative_target_is_not_the_newest_message():
    for index in range(20):
        s = chat.build(seed=0, kind="relative", index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_task_text_names_sender_and_fixed_topic():
    s = chat.build(seed=0, kind="fixed", index=0, variant="none")
    f = dict(s.criterion.filters)
    assert f["sender"] in s.task and f["topic"] in s.task


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError):
        chat.build(seed=0, kind="relative", index=0, variant="L2")
