"""Whether a change moved the task's target. Computed from the data, never labelled by hand."""
from typing import Sequence

from .criteria import Criterion
from .items import Item
from .resolve import resolve


def classify(before: Sequence[Item], after: Sequence[Item], criterion: Criterion) -> str:
    """Return "none" (items unchanged), "irrelevant" (target unchanged), "relevant" (target moved to another
    item) or "target_removed" (no unique target any more)."""
    if list(before) == list(after):
        return "none"
    old, new = resolve(before, criterion), resolve(after, criterion)
    if old.status != "unique":
        raise ValueError(f"no unique target before the change ({old.status})")
    if new.status != "unique":
        return "target_removed"
    return "irrelevant" if new.target == old.target else "relevant"
