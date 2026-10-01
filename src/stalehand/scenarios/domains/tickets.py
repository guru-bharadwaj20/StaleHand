"""Tickets scenarios: assign a ticket chosen by key (fixed) or as the oldest high-priority ticket (relative), while
new tickets arrive, priorities change or a ticket is closed.

Variants (all share the same first screen for a given seed, kind and index):
  none       nothing changes
  cosmetic   a maintenance banner appears; no ticket changes
  new        three new tickets arrive at the top, one of them high priority
  escalate   an older, lower-priority ticket is raised to high
  downgrade  the target ticket is lowered to medium
  closed     the target ticket is closed and leaves the queue
"""
import random

from ..changes import Cosmetic, Insert, Remove, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .tickets_data import ASSIGNEES, REPORTERS, TITLES

N_ROWS = 10
N_ARRIVALS = 3
KINDS = ("fixed", "relative")
VARIANTS = ("none", "cosmetic", "new", "escalate", "downgrade", "closed")


def _ticket(number, title, priority, created, rng):
    return Item(f"t{number}", {"key": f"T-{number}", "title": title, "priority": priority,
                               "reporter": rng.choice(REPORTERS), "created": created, "assignee": None})


def _first_screen(rng):
    """Rows newest first. Two high-priority tickets; the target is the older one, with older tickets below it."""
    titles = rng.sample(TITLES, N_ROWS + N_ARRIVALS)
    priorities = [rng.choice(("medium", "low")) for _ in range(N_ROWS)]
    p = rng.randint(4, 7)
    priorities[p] = "high"
    priorities[rng.randint(0, p - 2)] = "high"
    first = rng.randint(1000, 8000)
    numbers = [first + N_ROWS - i for i in range(N_ROWS)]
    times = [11 * 60 + 42 - 37 * i - (7 * i) % 11 for i in range(N_ROWS)]
    items = [_ticket(numbers[i], titles[i], priorities[i], times[i], rng) for i in range(N_ROWS)]
    return items, titles, p, numbers[0]


def _arrivals(seed, kind, index, titles, newest):
    arng = random.Random(f"tickets-arrivals:{seed}:{kind}:{index}")
    priorities = ["high", "medium", "low"]
    arng.shuffle(priorities)
    times = [12 * 60 + 38 - 9 * k for k in range(N_ARRIVALS)]
    return tuple(_ticket(newest + N_ARRIVALS - k, titles[N_ROWS + k], priorities[k], times[k], arng)
                 for k in range(N_ARRIVALS))


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"tickets:{seed}:{kind}:{index}")
    items, titles, p, newest = _first_screen(rng)
    target = items[p]
    assignee = rng.choice(ASSIGNEES)
    if kind == "relative":
        criterion = Criterion({"priority": "high"}, Order("created", descending=False))
        task = f"Assign the oldest high-priority ticket to {assignee}."
    else:
        criterion = Criterion({"key": target.get("key")})
        task = f"Assign ticket {target.get('key')} to {assignee}."
    vrng = random.Random(f"tickets-change:{seed}:{kind}:{index}:{variant}")
    change = None
    if variant == "cosmetic":
        change = Cosmetic("maintenance_banner")
    elif variant == "new":
        change = Insert(_arrivals(seed, kind, index, titles, newest))
    elif variant == "escalate":
        change = Update(items[vrng.randint(p + 1, N_ROWS - 1)].id, {"priority": "high"})
    elif variant == "downgrade":
        change = Update(target.id, {"priority": "medium"})
    elif variant == "closed":
        change = Remove((target.id,))
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"tickets-{kind}-{index:03d}-{variant}", domain="tickets", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "action": "assign",
                          "recipient": assignee, "change_step": change_step})
