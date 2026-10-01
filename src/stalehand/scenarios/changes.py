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


@dataclass(frozen=True)
class Remove:
    ids: Tuple[str, ...]


@_applies(Remove)
def _remove(change: Remove, items: List[Item]) -> List[Item]:
    missing = set(change.ids) - {it.id for it in items}
    if missing:
        raise ValueError(f"cannot remove missing ids {sorted(missing)}")
    return [it for it in items if it.id not in change.ids]


@dataclass(frozen=True)
class Update:
    id: str
    attrs: Dict[str, object]


@_applies(Update)
def _update(change: Update, items: List[Item]) -> List[Item]:
    if change.id not in {it.id for it in items}:
        raise ValueError(f"cannot update missing id {change.id}")
    return [Item(it.id, {**it.attrs, **change.attrs}) if it.id == change.id else it for it in items]


@dataclass(frozen=True)
class Sort:
    field: str
    descending: bool = False


@_applies(Sort)
def _sort(change: Sort, items: List[Item]) -> List[Item]:
    present = sorted((it for it in items if it.get(change.field) is not None),
                     key=lambda it: it.get(change.field), reverse=change.descending)
    return present + [it for it in items if it.get(change.field) is None]


@dataclass(frozen=True)
class Cosmetic:
    """A change to the page that touches no item, such as a banner or a toast. Guards may still notice it."""
    label: str


@_applies(Cosmetic)
def _cosmetic(change: Cosmetic, items: List[Item]) -> List[Item]:
    return items
