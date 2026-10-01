from stalehand.scenarios.changes import Cosmetic, Insert, Remove, Update, apply
from stalehand.scenarios.criteria import Criterion, Order
from stalehand.scenarios.items import Item
from stalehand.scenarios.relevance import classify

LATEST_SAM = Criterion({"sender": "Sam"}, Order("received"))
CHEAPEST = Criterion(order=Order("price", descending=False))
INBOX = [Item("a", {"sender": "Sam", "received": 10}), Item("b", {"sender": "Kim", "received": 20})]
SHOP = [Item("p1", {"price": 300}), Item("p2", {"price": 500})]


def after(items, change):
    return apply(items, change)


def test_newer_mail_from_sender_is_relevant():
    new = after(INBOX, Insert((Item("n", {"sender": "Sam", "received": 30}),)))
    assert classify(INBOX, new, LATEST_SAM) == "relevant"


def test_mail_from_other_sender_is_irrelevant():
    new = after(INBOX, Insert((Item("n", {"sender": "Kim", "received": 30}),)))
    assert classify(INBOX, new, LATEST_SAM) == "irrelevant"


def test_cosmetic_change_is_none():
    assert classify(INBOX, after(INBOX, Cosmetic("banner")), LATEST_SAM) == "none"


def test_removing_the_only_target_is_target_removed():
    assert classify(INBOX, after(INBOX, Remove(("a",))), LATEST_SAM) == "target_removed"


def test_price_drop_below_cheapest_is_relevant():
    assert classify(SHOP, after(SHOP, Update("p2", {"price": 100})), CHEAPEST) == "relevant"


def test_price_rise_on_other_item_is_irrelevant():
    assert classify(SHOP, after(SHOP, Update("p2", {"price": 900})), CHEAPEST) == "irrelevant"


def test_reordering_alone_is_irrelevant():
    assert classify(INBOX, list(reversed(INBOX)), LATEST_SAM) == "irrelevant"
