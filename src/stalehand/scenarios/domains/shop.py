"""Shop scenarios: add a product to the cart, chosen by name (fixed) or as the cheapest or highest-rated
listing (relative), while listings arrive, prices change or a product sells out.

Variants (all share the same first screen for a given seed, kind and index):
  none, cosmetic   nothing changes / a promo banner appears
  L0, L1, L3       three listings arrive at the top; 0, 1 or 3 of them beat the target on the task's attribute
  price_drop       another listing's price drops below the target's price
  sold_out         the target listing is removed
"""
import random

from ..changes import Cosmetic, Insert, Remove, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .shop_data import CATEGORIES

N_ROWS = 10
N_ARRIVALS = 3
KINDS = ("cheapest", "highest_rated", "fixed")
VARIANTS = ("none", "cosmetic", "L0", "L1", "L3", "price_drop", "sold_out")


def _listing(lid, name, category, price, rating, reviews):
    return Item(lid, {"name": name, "category": category, "price": price, "rating": rating, "reviews": reviews})


def _first_screen(rng, kind):
    category = rng.choice(sorted(CATEGORIES))
    names = rng.sample(CATEGORIES[category], N_ROWS + N_ARRIVALS)
    prices = [v * 25 - 1 for v in rng.sample(range(16, 60), N_ROWS)]
    ratings = [r / 10 for r in rng.sample(range(30, 45), N_ROWS)]
    p = rng.randint(2, 6)
    if kind == "cheapest":
        prices[p] = min(prices[:p] + prices[p + 1:]) - 50
    if kind == "highest_rated":
        ratings[p] = round(max(ratings[:p] + ratings[p + 1:]) + 0.1, 1)
    items = [_listing(f"p{i:02d}", names[i], category, prices[i], ratings[i], rng.randint(40, 9000))
             for i in range(N_ROWS)]
    return items, category, names, p


def _arrivals(variant, key, target, rng, names, category):
    beating = int(variant[1:])
    out = []
    for k in range(N_ARRIVALS):
        price = rng.randint(16, 60) * 25 - 1
        rating = round(rng.uniform(3.0, 4.0), 1)
        if key == "price":
            price = target.get("price") - 25 * (k + 1) if k < beating else target.get("price") + 200 + 25 * k
        elif key == "rating":
            rating = round(target.get("rating") + 0.1 * (k + 1), 1) if k < beating else round(target.get("rating") - 0.5 - 0.1 * k, 1)
        out.append(_listing(f"q{k}", names[N_ROWS + k], category, price, rating, rng.randint(40, 9000)))
    rng.shuffle(out)
    return tuple(out)


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"shop:{seed}:{kind}:{index}")
    items, category, names, p = _first_screen(rng, kind)
    target = items[p]
    if kind == "cheapest":
        criterion, task = Criterion(order=Order("price", descending=False)), f"Add the cheapest {category} on this page to the cart."
    elif kind == "highest_rated":
        criterion, task = Criterion(order=Order("rating", descending=True)), f"Add the highest-rated {category} on this page to the cart."
    else:
        criterion, task = Criterion({"name": target.get("name")}), f"Add the {target.get('name')} {category} to the cart."
    vrng = random.Random(f"shop-change:{seed}:{kind}:{index}:{variant}")
    change = None
    if variant == "cosmetic":
        change = Cosmetic("promo_banner")
    elif variant.startswith("L"):
        key = {"cheapest": "price", "highest_rated": "rating"}.get(kind)
        change = Insert(_arrivals(variant if key else "L0", key, target, vrng, names, category))
    elif variant == "price_drop":
        other = items[vrng.choice([i for i in range(N_ROWS) if i != p])]
        change = Update(other.id, {"price": target.get("price") - 50 if kind == "cheapest"
                                   else min(it.get("price") for it in items) - 50})
    elif variant == "sold_out":
        change = Remove((target.id,))
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"shop-{kind}-{index:03d}-{variant}", domain="shop", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "category": category,
                          "action": "add_to_cart", "change_step": change_step})
