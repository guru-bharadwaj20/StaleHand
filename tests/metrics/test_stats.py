import math

import pytest

from stalehand.metrics import stats


def test_mcnemar_known_values():
    assert stats.mcnemar_exact(0, 10) == pytest.approx(2 / 1024)
    assert stats.mcnemar_exact(1, 9) == pytest.approx(22 / 1024)
    assert stats.mcnemar_exact(5, 5) == 1.0
    assert stats.mcnemar_exact(0, 0) == 1.0


def test_mcnemar_is_symmetric():
    assert stats.mcnemar_exact(3, 17) == stats.mcnemar_exact(17, 3)


def test_mcnemar_matches_scipy():
    scipy_stats = pytest.importorskip("scipy.stats")
    for b, c in [(2, 30), (7, 12), (40, 60), (0, 1)]:
        assert stats.mcnemar_exact(b, c) == pytest.approx(scipy_stats.binomtest(b, b + c, 0.5).pvalue)


def test_mcnemar_large_counts_do_not_overflow():
    p = stats.mcnemar_exact(400, 600)
    assert 0 < p < 1e-9 and math.isfinite(p)


def row(sid, outcome, guard="g"):
    return {"scenario_id": sid, "outcome": outcome, "guard": guard}


def test_template_drops_the_variant():
    assert stats.template_of("inbox-relative-007-L3") == "inbox-relative-007"
    assert stats.template_of("shop-highest_rated-012-price_drop") == "shop-highest_rated-012"


def test_pairs_only_shared_scenarios_and_counts_missing():
    a = [row("x-k-000-L1", "success"), row("x-k-001-L1", "stale")]
    b = [row("x-k-000-L1", "stale"), row("x-k-002-L1", "success")]
    pairs, missing = stats.pair(a, b)
    assert pairs == [("x-k-000-L1", True, False)] and missing == {"only_a": 1, "only_b": 1}


def test_duplicate_scenario_in_one_arm_is_an_error():
    with pytest.raises(ValueError):
        stats.pair([row("x-k-000-L1", "success")] * 2, [row("x-k-000-L1", "success")])


def mean(xs):
    return sum(xs) / len(xs)


def test_bootstrap_is_deterministic_for_a_seed():
    units = [(f"t{i // 3}", i % 2) for i in range(60)]
    f = lambda us: mean([u[1] for u in us])
    assert stats.cluster_bootstrap(units, f, lambda u: u[0], n_boot=300, seed=1) == \
        stats.cluster_bootstrap(units, f, lambda u: u[0], n_boot=300, seed=1)


def test_constant_data_gives_point_interval():
    units = [(f"t{i}", 1) for i in range(20)]
    lo, hi = stats.cluster_bootstrap(units, lambda us: mean([u[1] for u in us]), lambda u: u[0], n_boot=200)
    assert lo == hi == 1


def test_interval_contains_estimate():
    units = [(f"t{i // 4}", 1 if i % 3 else 0) for i in range(120)]
    f = lambda us: mean([u[1] for u in us])
    lo, hi = stats.cluster_bootstrap(units, f, lambda u: u[0], n_boot=500)
    assert lo <= f(units) <= hi and lo < hi


def test_correlated_clusters_widen_the_interval():
    # every template is all-success or all-failure: 10 independent clusters, not 100 independent units
    units = [(f"t{i // 10}", (i // 10) % 2) for i in range(100)]
    f = lambda us: mean([u[1] for u in us])
    clustered = stats.cluster_bootstrap(units, f, lambda u: u[0], n_boot=1000)
    iid = stats.cluster_bootstrap(units, f, lambda u: id(u), n_boot=1000)
    assert clustered[1] - clustered[0] > 1.5 * (iid[1] - iid[0])
def test_compare_summarises_discordant_pairs():
    a = [row(f"x-k-{i:03d}-L1", "success") for i in range(12)]
    b = [row(f"x-k-{i:03d}-L1", "success" if i < 2 else "stale") for i in range(12)]
    r = stats.compare(a, b, n_boot=200)
    assert (r["n"], r["a_only"], r["b_only"]) == (12, 10, 0)
    assert r["a_rate"] == 1.0 and r["b_rate"] == pytest.approx(2 / 12)
    assert r["p"] == pytest.approx(stats.mcnemar_exact(10, 0))
