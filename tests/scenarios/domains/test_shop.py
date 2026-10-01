import pytest

from stalehand.scenarios.domains import shop
from stalehand.scenarios.serialize import scenario_to_dict

KINDS = ("cheapest", "highest_rated", "fixed")


def test_same_arguments_give_same_scenario():
    a, b = (shop.build(seed=0, kind="cheapest", index=3, variant="L1") for _ in range(2))
    assert scenario_to_dict(a) == scenario_to_dict(b)


@pytest.mark.parametrize("kind", KINDS)
def test_variants_share_the_first_screen(kind):
    firsts = [shop.build(seed=0, kind=kind, index=1, variant=v).items for v in shop.VARIANTS]
    assert all(f == firsts[0] for f in firsts)


@pytest.mark.parametrize("kind,variant,expected", [
    ("cheapest", "L1", "relevant"), ("cheapest", "L3", "relevant"), ("cheapest", "L0", "irrelevant"),
    ("highest_rated", "L1", "relevant"), ("highest_rated", "L0", "irrelevant"),
    ("cheapest", "price_drop", "relevant"), ("highest_rated", "price_drop", "irrelevant"),
    ("fixed", "L3", "irrelevant"), ("fixed", "price_drop", "irrelevant"),
    ("cheapest", "sold_out", "relevant"), ("fixed", "sold_out", "target_removed"),
    ("cheapest", "none", "none"), ("fixed", "cosmetic", "none")])
def test_change_kind_follows_variant(kind, variant, expected):
    for index in range(20):
        assert shop.build(seed=0, kind=kind, index=index, variant=variant).change_kind == expected


@pytest.mark.parametrize("kind", ("cheapest", "highest_rated"))
def test_relative_target_is_not_the_top_listing(kind):
    for index in range(20):
        s = shop.build(seed=0, kind=kind, index=index, variant="none")
        assert s.items[0].id != s.stale_target


def test_task_text_names_category():
    s = shop.build(seed=0, kind="cheapest", index=0, variant="none")
    assert s.meta["category"] in s.task and "cheapest" in s.task


def test_fixed_task_names_product():
    s = shop.build(seed=0, kind="fixed", index=0, variant="none")
    assert dict(s.criterion.filters)["name"] in s.task
