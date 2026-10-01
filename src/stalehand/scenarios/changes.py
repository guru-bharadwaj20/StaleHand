"""Changes that happen to the screen while the agent works. Each one is a pure function of the item list."""
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple, Type

from .items import Item

_APPLIERS: Dict[Type, Callable[[object, List[Item]], List[Item]]] = {}


def _applies(kind):
    def register(fn):
        _APPLIERS[kind] = fn
        return fn
    return register


def apply(items: Sequence[Item], change) -> List[Item]:
    try:
        fn = _APPLIERS[type(change)]
    except KeyError:
        raise TypeError(f"unknown change {type(change).__name__}") from None
    return fn(change, list(items))


@dataclass(frozen=True)
class Insert:
    items: Tuple[Item, ...]
    position: int = 0


@_applies(Insert)
def _insert(change: Insert, items: List[Item]) -> List[Item]:
    present = {it.id for it in items}
    clash = [it.id for it in change.items if it.id in present]
    if clash:
        raise ValueError(f"insert would duplicate ids {clash}")
    return items[:change.position] + list(change.items) + items[change.position:]
