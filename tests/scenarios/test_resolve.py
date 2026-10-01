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
