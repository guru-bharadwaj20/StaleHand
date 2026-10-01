import pytest

from stalehand.scenarios.changes import Insert, Update
from stalehand.scenarios.criteria import Criterion, Order
from stalehand.scenarios.items import Item
from stalehand.scenarios.scenario import Scenario, ScheduledChange


def make(changes=()):
    return Scenario(
        id="inbox-R-00-L1", domain="inbox", seed=0, task="Forward the latest email from Sam to Kim.",
        criterion=Criterion({"sender": "Sam"}, Order("received")),
        items=(Item("a", {"sender": "Sam", "received": 10}), Item("b", {"sender": "Kim", "received": 20})),
        changes=tuple(changes))


NEW = ScheduledChange(2, Insert((Item("n", {"sender": "Sam", "received": 30}),)))


def test_stale_target_is_resolved_on_initial_items():
    assert make([NEW]).stale_target == "a"


def test_target_before_change_step_is_unchanged():
    assert make([NEW]).target_at(1) == "a"


def test_target_from_change_step_onwards_moves():
    s = make([NEW])
    assert s.target_at(2) == "n" and s.target_at(5) == "n"


def test_changes_apply_in_step_order():
    later = ScheduledChange(3, Update("n", {"received": 5}))
    assert make([later, NEW]).target_at(3) == "a"


def test_change_kind_summarises_final_state():
    assert make([NEW]).change_kind == "relevant"
    assert make().change_kind == "none"


def test_scenario_without_unique_initial_target_is_rejected():
    with pytest.raises(ValueError):
        Scenario(id="x", domain="inbox", seed=0, task="t", criterion=Criterion({"sender": "Zed"}),
                 items=(Item("a", {"sender": "Sam"}),))


def test_negative_change_step_is_rejected():
    with pytest.raises(ValueError):
        ScheduledChange(-1, Insert(()))
