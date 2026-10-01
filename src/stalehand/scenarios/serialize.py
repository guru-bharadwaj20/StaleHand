"""JSON-safe dictionaries for scenario parts, so scenarios can be written to JSONL and read back exactly."""
from typing import Any, Dict

from .criteria import Criterion, Order
from .items import Item


def item_to_dict(item: Item) -> Dict[str, Any]:
    return {"id": item.id, "attrs": dict(item.attrs)}


def item_from_dict(d: Dict[str, Any]) -> Item:
    return Item(d["id"], d["attrs"])


def criterion_to_dict(c: Criterion) -> Dict[str, Any]:
    order = None if c.order is None else {"field": c.order.field, "descending": c.order.descending}
    return {"filters": [[k, v] for k, v in c.filters], "order": order}


def criterion_from_dict(d: Dict[str, Any]) -> Criterion:
    order = None if d["order"] is None else Order(d["order"]["field"], d["order"]["descending"])
    return Criterion(tuple((k, v) for k, v in d["filters"]), order)
