import pytest

from stalehand.scenarios.domains import tickets
from stalehand.scenarios.domains.tickets_data import TITLES
from stalehand.scenarios.serialize import scenario_to_dict

KINDS = ("fixed", "relative")


def test_title_pool_is_unique():
    assert len(set(TITLES)) == len(TITLES) == 40


def test_same_arguments_give_same_scenario():
    a, b = (tickets.build(seed=0, kind="relative", index=3, variant="escalate") for _ in range(2))
    assert scenario_to_dict(a) == scenario_to_dict(b)


@pytest.mark.parametrize("kind", KINDS)
def test_variants_share_the_first_screen(kind):
    firsts = [tickets.build(seed=0, kind=kind, index=1, variant=v).items for v in tickets.VARIANTS]
    assert all(f == firsts[0] for f in firsts)


def test_first_screen_has_ten_rows_newest_first():
    s = tickets.build(seed=0, kind="relative", index=0, variant="none")
    created = [it.get("created") for it in s.items]
    assert len(created) == 10 and created == sorted(created, reverse=True)


@pytest.mark.parametrize("kind,variant,expected", [
    ("relative", "escalate", "relevant"), ("relative", "downgrade", "relevant"), ("relative", "closed", "relevant"),
    ("relative", "new", "irrelevant"), ("fixed", "new", "irrelevant"), ("fixed", "escalate", "irrelevant"),
    ("fixed", "downgrade", "irrelevant"), ("fixed", "closed", "target_removed"),
    ("relative", "none", "none"), ("fixed", "cosmetic", "none")])
def test_change_kind_follows_variant(kind, variant, expected):
    for index in range(20):
        assert tickets.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


def test_relative_target_is_not_the_top_row():
    for index in range(20):
        s = tickets.build(seed=0, kind="relative", index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_keys_are_unique_after_arrivals():
    for index in range(20):
        s = tickets.build(seed=0, kind="fixed", index=index, variant="new")
        keys = [it.get("key") for it in s.items_at(s.last_change_step)]
        assert len(set(keys)) == len(keys)


def test_task_text_names_key_and_assignee():
    s = tickets.build(seed=0, kind="fixed", index=0, variant="none")
    assert dict(s.criterion.filters)["key"] in s.task and s.meta["recipient"] in s.task


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError):
        tickets.build(seed=0, kind="relative", index=0, variant="L1")
