"""A scenario: the task, the items the planner sees at step 0, and changes scheduled at later steps.

A change scheduled at step k is applied before the executor observes the screen at step k.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .changes import apply
from .criteria import Criterion
from .items import Item
from .relevance import classify
from .resolve import resolve


@dataclass(frozen=True)
class ScheduledChange:
    step: int
    change: Any

    def __post_init__(self):
        if self.step < 0:
            raise ValueError("change step must be >= 0")


@dataclass(frozen=True)
class Scenario:
    id: str
    domain: str
    seed: int
    task: str
    criterion: Criterion
    items: Tuple[Item, ...]
    changes: Tuple[ScheduledChange, ...] = ()
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "changes", tuple(sorted(self.changes, key=lambda c: c.step)))
        if resolve(self.items, self.criterion).status != "unique":
            raise ValueError(f"scenario {self.id} has no unique target on its first screen")

    def items_at(self, step: int) -> List[Item]:
        items = list(self.items)
        for sc in self.changes:
            if sc.step <= step:
                items = apply(items, sc.change)
        return items

    @property
    def last_change_step(self) -> int:
        return self.changes[-1].step if self.changes else 0

    @property
    def stale_target(self) -> str:
        return resolve(self.items, self.criterion).target

    def target_at(self, step: int):
        return resolve(self.items_at(step), self.criterion).target

    @property
    def change_kind(self) -> str:
        return classify(self.items, self.items_at(self.last_change_step), self.criterion)
