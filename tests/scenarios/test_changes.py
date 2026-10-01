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
