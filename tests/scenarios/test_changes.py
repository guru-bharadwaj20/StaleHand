import pytest

from stalehand.scenarios.changes import Insert, apply
from stalehand.scenarios.items import Item

BASE = [Item("a", {"v": 1}), Item("b", {"v": 2}), Item("c", {"v": 3})]


def ids(items):
    return [it.id for it in items]


def test_insert_defaults_to_top():
    out = apply(BASE, Insert((Item("n", {"v": 9}),)))
    assert ids(out) == ["n", "a", "b", "c"]


def test_insert_at_position():
    out = apply(BASE, Insert((Item("n", {}), Item("m", {})), position=2))
    assert ids(out) == ["a", "b", "n", "m", "c"]


def test_insert_duplicate_id_is_rejected():
    with pytest.raises(ValueError):
        apply(BASE, Insert((Item("a", {}),)))


def test_apply_does_not_mutate_input():
    apply(BASE, Insert((Item("n", {}),)))
    assert ids(BASE) == ["a", "b", "c"]


def test_remove_drops_ids():
    from stalehand.scenarios.changes import Remove
    assert ids(apply(BASE, Remove(("b",)))) == ["a", "c"]


def test_remove_missing_id_is_rejected():
    from stalehand.scenarios.changes import Remove
    with pytest.raises(ValueError):
        apply(BASE, Remove(("zz",)))


def test_update_merges_attributes():
    from stalehand.scenarios.changes import Update
    out = apply(BASE, Update("b", {"v": 20, "sale": True}))
    assert dict(out[1].attrs) == {"v": 20, "sale": True}
    assert out[0] is BASE[0] and out[2] is BASE[2]


def test_update_missing_id_is_rejected():
    from stalehand.scenarios.changes import Update
    with pytest.raises(ValueError):
        apply(BASE, Update("zz", {"v": 1}))


def test_sort_orders_by_field():
    from stalehand.scenarios.changes import Sort
    assert ids(apply(BASE, Sort("v", descending=True))) == ["c", "b", "a"]


def test_sort_puts_missing_field_last():
    from stalehand.scenarios.changes import Sort
    items = [Item("x", {}), Item("y", {"v": 1}), Item("z", {"v": 2})]
    assert ids(apply(items, Sort("v"))) == ["y", "z", "x"]
