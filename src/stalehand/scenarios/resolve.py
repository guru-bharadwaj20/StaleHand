"""Ground truth: which item does the task refer to, given the items on screen right now?"""
from dataclasses import dataclass
from typing import Iterable, Optional

from .criteria import Criterion
from .items import Item


@dataclass(frozen=True)
class Resolution:
    target: Optional[str]
    status: str  # "unique", "none" or "ambiguous"


def _matches(item: Item, criterion: Criterion) -> bool:
    return all(item.get(k) == v for k, v in criterion.filters)


def resolve(items: Iterable[Item], criterion: Criterion) -> Resolution:
    found = [it for it in items if _matches(it, criterion)]
    if not found:
        return Resolution(None, "none")
    if criterion.order is not None:
        return _pick_by_order(found, criterion)
    if len(found) > 1:
        return Resolution(None, "ambiguous")
    return Resolution(found[0].id, "unique")


def _pick_by_order(found, criterion: Criterion) -> Resolution:
    key = criterion.order.field
    found = [it for it in found if it.get(key) is not None]
    if not found:
        return Resolution(None, "none")
    pick = max if criterion.order.descending else min
    best = pick(it.get(key) for it in found)
    top = [it for it in found if it.get(key) == best]
    if len(top) > 1:
        return Resolution(None, "ambiguous")
    return Resolution(top[0].id, "unique")
