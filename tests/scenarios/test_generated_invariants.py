"""Invariants over many generated scenarios, so a generator bug cannot hide in one lucky seed."""
import pytest

from stalehand.scenarios import registry
from stalehand.scenarios.resolve import resolve


@pytest.mark.parametrize("domain", sorted(registry.DOMAINS))
@pytest.mark.parametrize("seed", range(5))
def test_targets_resolve_uniquely(domain, seed):
    for s in registry.generate(domain, seed=seed, n=10):
        final = resolve(s.items_at(s.last_change_step), s.criterion)
        if s.change_kind == "target_removed":
            assert final.status != "unique"
        else:
            assert final.status == "unique", s.id


@pytest.mark.parametrize("domain", sorted(registry.DOMAINS))
def test_item_ids_are_unique_on_every_screen(domain):
    for s in registry.generate(domain, seed=0, n=10):
        for step in range(s.last_change_step + 1):
            ids = [it.id for it in s.items_at(step)]
            assert len(ids) == len(set(ids)), s.id
