"""Files scenarios: share a file chosen by name (fixed) or as the newest file of a type (relative), while files
are uploaded or renamed.

Variants (all share the same first screen for a given seed, kind and index):
  none      nothing changes
  cosmetic  a storage banner appears; no file changes
  L0        three files are uploaded, none of the task's type
  L1, L3    three files are uploaded, one or three of them of the task's type
  rename    the target file is renamed (its type and modified time stay the same)
"""
import random

from ..changes import Cosmetic, Insert, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .files_data import OWNERS, RECIPIENTS, TYPES

N_ROWS = 10
N_ARRIVALS = 3
KINDS = ("fixed", "relative")
VARIANTS = ("none", "cosmetic", "L0", "L1", "L3", "rename")


def _file(fid, ftype, base, modified, rng, owner=None):
    ext = TYPES[ftype][0]
    return Item(fid, {"name": f"{base}.{ext}", "type": ftype, "owner": owner or rng.choice(OWNERS),
                      "modified": modified, "size_kb": rng.randint(40, 9000)})


def _first_screen(rng, kind):
    """Rows newest first. The target is the newest file of its type; relative tasks get a second, older one."""
    ftype, *others = rng.sample(sorted(TYPES), len(TYPES))
    pools = {t: iter(rng.sample(TYPES[t][1], len(TYPES[t][1]))) for t in TYPES}
    types = [others[i % len(others)] for i in range(N_ROWS)]
    p = rng.randint(1, 5)
    types[p] = ftype
    if kind == "relative":
        types[rng.randint(p + 2, N_ROWS - 1)] = ftype
    times = [11 * 60 + 42 - 23 * i - (7 * i) % 11 for i in range(N_ROWS)]
    items = [_file(f"f{i:02d}", t, next(pools[t]), times[i], rng) for i, t in enumerate(types)]
    return items, ftype, others, pools, p


def _uploads(variant, seed, kind, index, ftype, others, pools):
    urng = random.Random(f"files-uploads:{seed}:{kind}:{index}:{variant}")
    of_type = int(variant[1:])
    types = [ftype] * of_type + [others[k] for k in range(N_ARRIVALS - of_type)]
    urng.shuffle(types)
    times = [12 * 60 + 38 - 9 * k for k in range(N_ARRIVALS)]
    return tuple(_file(f"u{k}", t, next(pools[t]), times[k], urng, owner="me") for k, t in enumerate(types))


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"files:{seed}:{kind}:{index}")
    items, ftype, others, pools, p = _first_screen(rng, kind)
    target = items[p]
    recipient = rng.choice(RECIPIENTS)
    if kind == "relative":
        criterion = Criterion({"type": ftype}, Order("modified", descending=True))
        task = f"Share the newest {ftype} with {recipient}."
    else:
        criterion = Criterion({"name": target.get("name")})
        task = f"Share {target.get('name')} with {recipient}."
    change = None
    if variant == "cosmetic":
        change = Cosmetic("storage_banner")
    elif variant.startswith("L"):
        change = Insert(_uploads(variant, seed, kind, index, ftype, others, pools))
    elif variant == "rename":
        stem, ext = target.get("name").rsplit(".", 1)
        change = Update(target.id, {"name": f"{stem} (final).{ext}"})
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"files-{kind}-{index:03d}-{variant}", domain="files", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "type": ftype, "action": "share",
                          "recipient": recipient, "change_step": change_step})
