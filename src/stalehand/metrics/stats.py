"""Paired statistics for guard comparisons. Stdlib only, so every machine and CI job can run them."""
import math


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar test: binomial test of the discordant pairs (b, c) against p = 0.5."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # log-space sum keeps large n finite
    logs = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2) for i in range(k + 1)]
    top = max(logs)
    tail = math.exp(top) * sum(math.exp(v - top) for v in logs)
    return min(1.0, 2 * tail)
