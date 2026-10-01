"""Calendar scenarios: join a meeting chosen by title (fixed) or as the next meeting with a person (relative),
while meetings are added, rescheduled or cancelled.

The agenda lists today's upcoming meetings, earliest first. Variants (all share the same first screen for a given
seed, kind and index):
  none        nothing changes
  cosmetic    a reminder banner appears; no meeting changes
  L0, L1      three meetings are added before the target; none or one of them with the task's person
  reschedule  the target meeting moves to after the person's other meeting
  cancelled   the target meeting is cancelled and leaves the agenda
"""
import random

from ..changes import Cosmetic, Insert, Remove, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .calendar_data import PEOPLE, TITLES

N_ROWS = 8
N_ARRIVALS = 3
KINDS = ("fixed", "relative")
VARIANTS = ("none", "cosmetic", "L0", "L1", "reschedule", "cancelled")


def _meeting(mid, title, person, start, minutes):
    return Item(mid, {"title": title, "with": person, "start": start, "minutes": minutes})


def _first_screen(rng):
    """Meetings earliest first from 9:30. The target is the person's first meeting; their second comes later."""
    person, *others = rng.sample(PEOPLE, len(PEOPLE))
    titles = rng.sample(TITLES, N_ROWS + N_ARRIVALS)
    starts = [9 * 60 + 30 + 60 * i for i in range(N_ROWS)]
    people = [others[i] for i in range(N_ROWS)]
    p = rng.randint(2, 4)
    q = rng.randint(p + 2, N_ROWS - 1)
    people[p] = people[q] = person
    items = [_meeting(f"e{i:02d}", titles[i], people[i], starts[i], rng.choice((30, 45))) for i in range(N_ROWS)]
    return items, person, others, titles, p, q


def _additions(variant, seed, kind, index, person, others, titles, before):
    arng = random.Random(f"calendar-additions:{seed}:{kind}:{index}:{variant}")
    with_person = int(variant[1:])
    people = [person] * with_person + [others[N_ROWS + k] for k in range(N_ARRIVALS - with_person)]
    arng.shuffle(people)
    # 15-minute slots that end before the target starts, so the agenda stays readable
    return tuple(_meeting(f"a{k}", titles[N_ROWS + k], people[k], before - 15 * (N_ARRIVALS - k) - 15, 15)
                 for k in range(N_ARRIVALS))


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"calendar:{seed}:{kind}:{index}")
    items, person, others, titles, p, q = _first_screen(rng)
    target = items[p]
    if kind == "relative":
        criterion = Criterion({"with": person}, Order("start", descending=False))
        task = f"Join the next meeting with {person}."
    else:
        criterion = Criterion({"title": target.get("title")})
        task = f"Join the {target.get('title')} meeting."
    change = None
    if variant == "cosmetic":
        change = Cosmetic("reminder_banner")
    elif variant.startswith("L"):
        change = Insert(_additions(variant, seed, kind, index, person, others, titles, target.get("start")), position=p)
    elif variant == "reschedule":
        change = Update(target.id, {"start": items[q].get("start") + 30})
    elif variant == "cancelled":
        change = Remove((target.id,))
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"calendar-{kind}-{index:03d}-{variant}", domain="calendar", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "person": person, "action": "join",
                          "change_step": change_step})
