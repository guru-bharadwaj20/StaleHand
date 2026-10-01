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
    if len(found) > 1:
        return Resolution(None, "ambiguous")
    return Resolution(found[0].id, "unique")
