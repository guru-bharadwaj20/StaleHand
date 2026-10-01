"""Look up scenario generators by domain name and build whole scenario sets."""
from typing import Iterable, List, Optional

from .domains import inbox, shop
from .scenario import Scenario

DOMAINS = {"inbox": inbox, "shop": shop}


def generate(domain: str, seed: int, n: int, kinds: Optional[Iterable[str]] = None,
             variants: Optional[Iterable[str]] = None, change_step: int = 1) -> List[Scenario]:
    if domain not in DOMAINS:
        raise KeyError(f"unknown domain {domain!r}; known: {sorted(DOMAINS)}")
    mod = DOMAINS[domain]
    kinds = list(kinds or mod.KINDS)
    variants = list(variants or mod.VARIANTS)
    return [mod.build(seed=seed, kind=k, index=i, variant=v, change_step=change_step)
            for k in kinds for i in range(n) for v in variants]
