"""Paired statistics for guard comparisons. Stdlib only, so every machine and CI job can run them."""
import math
import random


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


def template_of(scenario_id: str) -> str:
    """Scenarios built from the same first screen share a template: the id without its variant suffix."""
    return scenario_id.rsplit("-", 1)[0]


def _ok(r: dict) -> bool:
    return r["outcome"] == "success"


def pair(rows_a, rows_b, success=_ok):
    """Match two arms by scenario id: ([(id, a_success, b_success), ...] sorted by id, missing counts)."""
    def index(rows):
        out = {}
        for r in rows:
            if r["scenario_id"] in out:
                raise ValueError(f"scenario {r['scenario_id']} appears twice in one arm")
            out[r["scenario_id"]] = r
        return out
    a, b = index(rows_a), index(rows_b)
    shared = sorted(a.keys() & b.keys())
    return ([(k, success(a[k]), success(b[k])) for k in shared],
            {"only_a": len(a.keys() - b.keys()), "only_b": len(b.keys() - a.keys())})


def cluster_bootstrap(units, stat, cluster_of, n_boot: int = 10000, seed: int = 0, alpha: float = 0.05):
    """Percentile interval for stat(units), resampling whole clusters with replacement.

    Scenarios from one template are not independent, so templates are the resampling unit."""
    clusters = {}
    for u in units:
        clusters.setdefault(cluster_of(u), []).append(u)
    groups = [clusters[k] for k in sorted(clusters, key=str)]
    rng = random.Random(seed)
    values = []
    for _ in range(n_boot):
        sample = []
        for _ in range(len(groups)):
            sample.extend(groups[rng.randrange(len(groups))])
        values.append(stat(sample))
    values.sort()
    lo = values[int(math.floor(alpha / 2 * (n_boot - 1)))]
    hi = values[int(math.ceil((1 - alpha / 2) * (n_boot - 1)))]
    return lo, hi
