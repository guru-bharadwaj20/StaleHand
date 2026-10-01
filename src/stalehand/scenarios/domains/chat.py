"""Chat scenarios: reply to a message chosen by sender and topic (fixed) or as the latest message from a sender
(relative), while new messages arrive or a message is edited.

Variants (all share the same first screen for a given seed, kind and index):
  none      nothing changes
  cosmetic  a "new messages" banner appears; no message changes
  L0        three messages arrive from other people
  L1, L3    three messages arrive, one or three of them from the task's sender
  edited    the sender edits the target message to be about something else (its time stays the same)
"""
import random

from ..changes import Cosmetic, Insert, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .inbox_data import SENDERS, TOPICS

N_ROWS = 10
N_ARRIVALS = 3
KINDS = ("fixed", "relative")
VARIANTS = ("none", "cosmetic", "L0", "L1", "L3", "edited")

OPENERS = ("Quick question about the {t}?", "Any news on the {t}?", "Can you look at the {t} today?",
           "I just updated the {t}.", "Heads up on the {t}.", "Thoughts on the {t}?")


def _message(mid, sender, topic, sent, rng, edited=False):
    return Item(mid, {"sender": sender, "topic": topic, "text": rng.choice(OPENERS).format(t=topic), "sent": sent,
                      "edited": edited})


def _first_screen(rng, kind):
    """Messages stored newest first (the app shows them oldest at the top, as chats do)."""
    sender, *others = rng.sample(SENDERS, len(SENDERS))
    topics = [t for t, _ in rng.sample(TOPICS, len(TOPICS))]
    rows = [(others[i], topics[i]) for i in range(N_ROWS)]
    p = rng.randint(1, 5)
    rows[p] = (sender, topics[20])
    if kind == "relative":
        rows[rng.randint(p + 2, N_ROWS - 1)] = (sender, topics[21])
    times = [11 * 60 + 42 - 13 * i - (7 * i) % 5 for i in range(N_ROWS)]
    items = [_message(f"c{i:02d}", s, t, times[i], rng) for i, (s, t) in enumerate(rows)]
    return items, sender, others, topics, p


def _arrivals(variant, seed, kind, index, sender, others, topics):
    arng = random.Random(f"chat-arrivals:{seed}:{kind}:{index}:{variant}")
    from_sender = int(variant[1:])
    new = [(sender, topics[30 + k]) for k in range(from_sender)]
    new += [(others[20 + k], topics[40 + k]) for k in range(from_sender, N_ARRIVALS)]
    arng.shuffle(new)
    times = [11 * 60 + 58 - 4 * k for k in range(N_ARRIVALS)]
    return tuple(_message(f"n{k}", s, t, times[k], arng) for k, (s, t) in enumerate(new))


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"chat:{seed}:{kind}:{index}")
    items, sender, others, topics, p = _first_screen(rng, kind)
    target = items[p]
    if kind == "relative":
        criterion = Criterion({"sender": sender}, Order("sent", descending=True))
        task = f"Reply to the latest message from {sender}."
    else:
        criterion = Criterion({"sender": sender, "topic": target.get("topic")})
        task = f"Reply to {sender}'s message about the {target.get('topic')}."
    change = None
    if variant == "cosmetic":
        change = Cosmetic("new_messages_banner")
    elif variant.startswith("L"):
        change = Insert(_arrivals(variant, seed, kind, index, sender, others, topics))
    elif variant == "edited":
        new_topic = topics[25]
        change = Update(target.id, {"topic": new_topic, "text": f"Sorry, wrong thread. About the {new_topic}?",
                                    "edited": True})
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"chat-{kind}-{index:03d}-{variant}", domain="chat", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "action": "reply",
                          "change_step": change_step})
