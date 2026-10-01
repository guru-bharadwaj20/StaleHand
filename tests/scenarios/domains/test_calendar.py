import pytest

from stalehand.scenarios.domains import calendar
from stalehand.scenarios.domains.calendar_data import PEOPLE, TITLES
from stalehand.scenarios.serialize import scenario_to_dict

KINDS = ("fixed", "relative")


def test_pools_are_unique():
    assert len(set(PEOPLE)) == len(PEOPLE) and len(set(TITLES)) == len(TITLES)


def test_same_arguments_give_same_scenario():
    a, b = (calendar.build(seed=0, kind="relative", index=3, variant="L1") for _ in range(2))
    assert scenario_to_dict(a) == scenario_to_dict(b)


@pytest.mark.parametrize("kind", KINDS)
def test_variants_share_the_first_screen(kind):
    firsts = [calendar.build(seed=0, kind=kind, index=1, variant=v).items for v in calendar.VARIANTS]
    assert all(f == firsts[0] for f in firsts)


@pytest.mark.parametrize("variant", calendar.VARIANTS)
def test_agenda_stays_earliest_first(variant):
    for index in range(10):
        s = calendar.build(seed=0, kind="relative", index=index, variant=variant)
        starts = [it.get("start") for it in s.items_at(s.last_change_step)]
        assert starts == sorted(starts) or variant == "reschedule"


@pytest.mark.parametrize("kind,variant,expected", [
    ("relative", "L1", "relevant"), ("relative", "L0", "irrelevant"), ("relative", "reschedule", "relevant"),
    ("relative", "cancelled", "relevant"), ("fixed", "L1", "irrelevant"), ("fixed", "L0", "irrelevant"),
    ("fixed", "reschedule", "irrelevant"), ("fixed", "cancelled", "target_removed"),
    ("relative", "none", "none"), ("fixed", "cosmetic", "none")])
def test_change_kind_follows_variant(kind, variant, expected):
    for index in range(20):
        assert calendar.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


def test_relative_target_is_not_the_top_row():
    for index in range(20):
        s = calendar.build(seed=0, kind="relative", index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_task_text_names_person_or_title():
    rel = calendar.build(seed=0, kind="relative", index=0, variant="none")
    fixed = calendar.build(seed=0, kind="fixed", index=0, variant="none")
    assert rel.meta["person"] in rel.task and dict(fixed.criterion.filters)["title"] in fixed.task


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError):
        calendar.build(seed=0, kind="relative", index=0, variant="L3")
