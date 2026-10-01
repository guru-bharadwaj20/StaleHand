import pytest

from stalehand.scenarios.criteria import Criterion, Order


def test_fixed_criterion_is_not_relative():
    assert not Criterion(filters=(("sender", "A"), ("subject", "Invoice"))).is_relative


def test_ordered_criterion_is_relative():
    assert Criterion(filters=(("sender", "A"),), order=Order("received", descending=True)).is_relative


def test_order_defaults_to_descending():
    assert Order("received").descending


def test_filters_given_as_dict_are_normalised():
    c = Criterion(filters={"sender": "A", "folder": "Inbox"})
    assert c.filters == (("folder", "Inbox"), ("sender", "A"))


def test_criterion_needs_filters_or_order():
    with pytest.raises(ValueError):
        Criterion(filters=())
