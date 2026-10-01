"""Look up scenario generators by domain name and build whole scenario sets."""
from typing import Iterable, List, Optional

import importlib
import pkgutil

from . import domains as _domains
from .scenario import Scenario


def _discover():
    """Every module in scenarios/domains/ that defines build, KINDS and VARIANTS is a domain."""
    found = {}
    for info in pkgutil.iter_modules(_domains.__path__):
        mod = importlib.import_module(f"{_domains.__name__}.{info.name}")
        if all(hasattr(mod, a) for a in ("build", "KINDS", "VARIANTS")):
            found[info.name] = mod
    return found


DOMAINS = _discover()


def generate(domain: str, seed: int, n: int, kinds: Optional[Iterable[str]] = None,
             variants: Optional[Iterable[str]] = None, change_step: int = 1) -> List[Scenario]:
    if domain not in DOMAINS:
        raise KeyError(f"unknown domain {domain!r}; known: {sorted(DOMAINS)}")
    mod = DOMAINS[domain]
    kinds = list(kinds or mod.KINDS)
    variants = list(variants or mod.VARIANTS)
    return [mod.build(seed=seed, kind=k, index=i, variant=v, change_step=change_step)
            for k in kinds for i in range(n) for v in variants]
