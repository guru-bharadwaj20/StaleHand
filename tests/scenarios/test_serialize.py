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
