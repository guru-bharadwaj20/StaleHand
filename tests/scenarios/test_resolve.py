from stalehand.scenarios.criteria import Criterion, Order
from stalehand.scenarios.items import Item
from stalehand.scenarios.resolve import resolve


def mail(i, sender, subject="s", received=0):
    return Item(i, {"sender": sender, "subject": subject, "received": received})


INBOX = [mail("a", "Samuel Lee", "Invoice", 10), mail("b", "Grace Kim", "Lunch", 20),
         mail("c", "Samuel Lee", "Budget", 30)]


def test_filters_select_single_match():
    r = resolve(INBOX, Criterion({"sender": "Samuel Lee", "subject": "Budget"}))
    assert (r.target, r.status) == ("c", "unique")


def test_no_match_gives_none():
    r = resolve(INBOX, Criterion({"sender": "Nobody"}))
    assert (r.target, r.status) == (None, "none")


def test_two_matches_without_order_are_ambiguous():
    r = resolve(INBOX, Criterion({"sender": "Samuel Lee"}))
    assert (r.target, r.status) == (None, "ambiguous")


def test_newest_first_picks_latest_from_sender():
    r = resolve(INBOX, Criterion({"sender": "Samuel Lee"}, Order("received")))
    assert (r.target, r.status) == ("c", "unique")


def test_ascending_order_picks_minimum():
    shop = [Item("p1", {"price": 499}), Item("p2", {"price": 299}), Item("p3", {"price": 899})]
    r = resolve(shop, Criterion(order=Order("price", descending=False)))
    assert r.target == "p2"


def test_order_without_filters_considers_every_item():
    r = resolve(INBOX, Criterion(order=Order("received")))
    assert r.target == "c"


def test_tie_at_the_top_is_ambiguous():
    shop = [Item("p1", {"price": 299}), Item("p2", {"price": 299}), Item("p3", {"price": 899})]
    r = resolve(shop, Criterion(order=Order("price", descending=False)))
    assert (r.target, r.status) == (None, "ambiguous")


def test_tie_below_the_top_does_not_matter():
    shop = [Item("p1", {"price": 199}), Item("p2", {"price": 299}), Item("p3", {"price": 299})]
    r = resolve(shop, Criterion(order=Order("price", descending=False)))
    assert (r.target, r.status) == ("p1", "unique")
