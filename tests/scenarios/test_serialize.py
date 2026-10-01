import json

from stalehand.scenarios import serialize as S
from stalehand.scenarios.criteria import Criterion, Order
from stalehand.scenarios.items import Item


def roundtrip(obj, dump, load):
    return load(json.loads(json.dumps(dump(obj))))


def test_item_roundtrip():
    it = Item("e1", {"sender": "Sam", "received": 10})
    assert roundtrip(it, S.item_to_dict, S.item_from_dict) == it


def test_fixed_criterion_roundtrip():
    c = Criterion({"sender": "Sam", "subject": "Invoice"})
    assert roundtrip(c, S.criterion_to_dict, S.criterion_from_dict) == c


def test_relative_criterion_roundtrip():
    c = Criterion({"sender": "Sam"}, Order("received", descending=True))
    assert roundtrip(c, S.criterion_to_dict, S.criterion_from_dict) == c


import pytest

from stalehand.scenarios.changes import Cosmetic, Insert, Remove, Sort, Update

CHANGES = [Insert((Item("n", {"sender": "Sam"}),), position=1), Remove(("a", "b")),
           Update("p1", {"price": 199}), Sort("price", descending=True), Cosmetic("toast")]


@pytest.mark.parametrize("change", CHANGES, ids=lambda c: type(c).__name__)
def test_change_roundtrip(change):
    assert roundtrip(change, S.change_to_dict, S.change_from_dict) == change


def test_unknown_change_type_is_rejected():
    with pytest.raises(ValueError):
        S.change_from_dict({"type": "explode"})
