import dataclasses

import pytest

from stalehand.scenarios.items import Item


def test_get_returns_attribute():
    item = Item("e1", {"sender": "Samuel Lee"})
    assert item.get("sender") == "Samuel Lee"


def test_get_missing_attribute_is_none():
    assert Item("e1", {}).get("price") is None


def test_item_is_frozen():
    item = Item("e1", {"sender": "A"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.id = "e2"


def test_attrs_are_copied_from_caller():
    attrs = {"sender": "A"}
    item = Item("e1", attrs)
    attrs["sender"] = "B"
    assert item.get("sender") == "A"


def test_attrs_cannot_be_mutated():
    item = Item("e1", {"sender": "A"})
    with pytest.raises(TypeError):
        item.attrs["sender"] = "B"
