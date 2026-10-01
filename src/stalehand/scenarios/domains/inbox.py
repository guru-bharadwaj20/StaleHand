"""Inbox scenarios: forward, reply to or open an email chosen by sender and topic (fixed) or by sender and
recency (relative), while new mail arrives.

Variants (all share the same first screen for a given seed, kind and index):
  none      nothing changes
  cosmetic  a banner appears; no email changes
  L0        three emails arrive from other senders
  L1, L3    three emails arrive, one or three of them from the task's sender
"""
import random

from ..changes import Cosmetic, Insert
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .inbox_data import RECIPIENTS, SENDERS, SNIPPETS, TOPICS

N_ROWS = 10
N_ARRIVALS = 3
VARIANTS = ("none", "cosmetic", "L0", "L1", "L3")
KINDS = ("fixed", "relative")

FIXED_TASKS = (
    ("forward", "Forward the email from {s} about the {t} to {r}."),
    ("reply", "Reply to the email from {s} about the {t} and thank them."),
    ("open", "Open the email from {s} about the {t}."),
)
RELATIVE_TASKS = (
    ("forward", "Forward the latest email from {s} to {r}."),
    ("reply", "Reply to the most recent email from {s} and thank them."),
    ("open", "Open the newest email from {s}."),
)


def _mail(mid, sender, topic, received, rng, unread=None):
    return Item(mid, {"sender": sender, "topic": topic[0], "subject": topic[1], "snippet": rng.choice(SNIPPETS),
                      "received": received, "unread": rng.random() < 0.35 if unread is None else unread})


def _first_screen(rng, kind):
    senders = rng.sample(SENDERS, len(SENDERS))
    sender, others = senders[0], senders[1:]
    topics = rng.sample(TOPICS, len(TOPICS))
    times = [11 * 60 + 42 - 23 * i - (7 * i) % 11 for i in range(N_ROWS)]
    rows = [(others[i], topics[i]) for i in range(N_ROWS)]
    p = rng.randint(1, 5)
    rows[p] = (sender, topics[20])
    if kind == "relative":
        rows[rng.randint(p + 2, N_ROWS - 1)] = (sender, topics[21])
    items = [_mail(f"m{i:02d}", s, t, times[i], rng) for i, (s, t) in enumerate(rows)]
    return items, sender, others, topics


def _arrivals(variant, seed, kind, index, sender, others, topics):
    lrng = random.Random(f"inbox-arrivals:{seed}:{kind}:{index}:{variant}")
    from_sender = int(variant[1:])
    new = [(sender, topics[30 + k]) for k in range(from_sender)]
    new += [(others[20 + k], topics[40 + k]) for k in range(from_sender, N_ARRIVALS)]
    lrng.shuffle(new)
    times = [12 * 60 + 38 - 9 * k for k in range(N_ARRIVALS)]
    return tuple(_mail(f"n{k}", s, t, times[k], lrng, unread=True) for k, (s, t) in enumerate(new))


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"inbox:{seed}:{kind}:{index}")
    items, sender, others, topics = _first_screen(rng, kind)
    action, template = rng.choice(RELATIVE_TASKS if kind == "relative" else FIXED_TASKS)
    recipient = rng.choice(RECIPIENTS)
    task = template.format(s=sender, t=topics[20][0], r=recipient)
    if kind == "relative":
        criterion = Criterion({"sender": sender}, Order("received", descending=True))
    else:
        criterion = Criterion({"sender": sender, "topic": topics[20][0]})
    changes = ()
    if variant == "cosmetic":
        changes = (ScheduledChange(change_step, Cosmetic("storage_banner")),)
    elif variant.startswith("L"):
        changes = (ScheduledChange(change_step, Insert(_arrivals(variant, seed, kind, index, sender, others, topics))),)
    return Scenario(id=f"inbox-{kind}-{index:03d}-{variant}", domain="inbox", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "action": action,
                          "recipient": recipient if action == "forward" else None, "change_step": change_step})
