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
