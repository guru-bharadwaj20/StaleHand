import pytest

from stalehand.scenarios import registry


def test_known_domains():
    assert {"inbox", "shop", "files"} <= set(registry.DOMAINS)


def test_generate_covers_every_kind_and_variant():
    out = registry.generate("inbox", seed=0, n=3)
    assert len(out) == 3 * 2 * 5 and len({s.id for s in out}) == len(out)


def test_generate_can_restrict_kinds_and_variants():
    out = registry.generate("shop", seed=0, n=2, kinds=["cheapest"], variants=["L1", "none"])
    assert {(s.meta["kind"], s.meta["variant"]) for s in out} == {("cheapest", "L1"), ("cheapest", "none")}


def test_more_scenarios_keep_earlier_ones_unchanged():
    small = {s.id: s for s in registry.generate("inbox", seed=0, n=2)}
    large = {s.id: s for s in registry.generate("inbox", seed=0, n=5)}
    assert all(large[k] == v for k, v in small.items())


def test_unknown_domain_is_rejected():
    with pytest.raises(KeyError):
        registry.generate("bank", seed=0, n=1)
