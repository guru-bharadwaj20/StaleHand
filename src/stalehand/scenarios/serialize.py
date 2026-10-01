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


def change_to_dict(change) -> Dict[str, Any]:
    from . import changes as C
    if isinstance(change, C.Insert):
        return {"type": "insert", "items": [item_to_dict(i) for i in change.items], "position": change.position}
    if isinstance(change, C.Remove):
        return {"type": "remove", "ids": list(change.ids)}
    if isinstance(change, C.Update):
        return {"type": "update", "id": change.id, "attrs": dict(change.attrs)}
    if isinstance(change, C.Sort):
        return {"type": "sort", "field": change.field, "descending": change.descending}
    if isinstance(change, C.Cosmetic):
        return {"type": "cosmetic", "label": change.label}
    raise TypeError(f"cannot serialise {type(change).__name__}")


def change_from_dict(d: Dict[str, Any]):
    from . import changes as C
    kind = d.get("type")
    if kind == "insert":
        return C.Insert(tuple(item_from_dict(i) for i in d["items"]), d["position"])
    if kind == "remove":
        return C.Remove(tuple(d["ids"]))
    if kind == "update":
        return C.Update(d["id"], d["attrs"])
    if kind == "sort":
        return C.Sort(d["field"], d["descending"])
    if kind == "cosmetic":
        return C.Cosmetic(d["label"])
    raise ValueError(f"unknown change type {kind!r}")
