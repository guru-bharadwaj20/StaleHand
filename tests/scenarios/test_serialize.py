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


def test_scenario_roundtrip():
    from stalehand.scenarios.scenario import Scenario, ScheduledChange
    s = Scenario(id="inbox-R-01-L1", domain="inbox", seed=3, task="Forward the latest email from Sam.",
                 criterion=Criterion({"sender": "Sam"}, Order("received")),
                 items=(Item("a", {"sender": "Sam", "received": 10}),),
                 changes=(ScheduledChange(2, Insert((Item("n", {"sender": "Sam", "received": 30}),))),),
                 meta={"task_kind": "relative", "level": 1})
    back = roundtrip(s, S.scenario_to_dict, S.scenario_from_dict)
    assert back == s and back.target_at(2) == "n"
