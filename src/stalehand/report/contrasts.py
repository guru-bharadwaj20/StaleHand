"""Paired contrasts across run sets: the same scenarios and guard under another architecture or change timing.

The guard report (build.py) compares guards inside one run set. These tables answer the other questions: does
delegating hurt, does a mid-step change hurt more than a handoff change, does the stall return help.
"""
import json
from pathlib import Path
from typing import List, Sequence

from ..metrics.stats import compare, holm, pair
from .build import _p, _pct, _table
from .tables import HARMLESS

SUBSETS = {"all": lambda r: True, "relevant": lambda r: r["change_kind"] == "relevant",
           "harmless": lambda r: r["change_kind"] in HARMLESS}
AXES = (("architecture", "hierarchical", ("guard", "timing"), "Architecture"),
        ("timing", "after_handoff", ("architecture", "guard"), "Change timing"))


def load_runs(root) -> List[dict]:
    """Every result row under root, tagged with the change timing of the job that wrote it."""
    rows = []
    for path in sorted(Path(root).rglob("results.jsonl")):
        cfg = path.parent / "config.json"
        timing = json.loads(cfg.read_text())["job"].get("change_timing") if cfg.exists() else None
        rows += [dict(json.loads(line), timing=timing) for line in path.read_text().splitlines() if line.strip()]
    return rows


def contrasts(rows, axis: str, base: str, within: Sequence[str], n_boot: int = 10000, seed: int = 0) -> List[dict]:
    """Each value of axis against base, paired by scenario inside each group of `within`, on all episodes and on
    the relevant and harmless subsets. Groups without shared scenarios are left out. p_holm adjusts over every
    comparison returned."""
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r.get(k) for k in within), {}).setdefault(r.get(axis), []).append(r)
    out = []
    for arm in sorted({r.get(axis) for r in rows} - {base}, key=str):
        for key in sorted(groups, key=lambda k: tuple(map(str, k))):
            arms = groups[key]
            if arm not in arms or base not in arms:
                continue
            for subset, keep in SUBSETS.items():
                a = [r for r in arms[arm] if keep(r)]
                b = [r for r in arms[base] if keep(r)]
                if not pair(a, b)[0]:
                    continue
                c = compare(a, b, n_boot=n_boot, seed=seed)
                out.append({"axis": axis, "arm": arm, "base": base, **dict(zip(within, key)), "subset": subset, **c})
    for c, p in zip(out, holm([c["p"] for c in out])):
        c["p_holm"] = p
    return out


def markdown(rows, n_boot: int = 10000, seed: int = 0) -> str:
    out = [f"Built from {len(rows)} scored episodes. Each table pairs episodes by scenario: same tasks, same guard, "
           "one thing changed. Difference is the arm's success rate minus the reference's, with a 95% bootstrap "
           f"interval over scenario templates ({n_boot} resamples, seed {seed}) and an exact McNemar test. The Holm "
           "column adjusts p over every comparison on the same axis.", ""]
    for axis, base, within, title in AXES:
        found = contrasts(rows, axis, base, within, n_boot=n_boot, seed=seed)
        for arm in dict.fromkeys(c["arm"] for c in found):
            out += [f"## {title}: `{arm}` against `{base}`", ""]
            out += _table([*within, "subset", "pairs", base, arm, "difference", "95% CI",
                           f"only {arm} vs only {base} succeeded", "McNemar", "Holm"],
                          [[*[str(c[k]) for k in within], c["subset"], str(c["n"]), _pct(c["b_rate"]),
                            _pct(c["a_rate"]), f"{100 * c['diff']:+.0f} pts",
                            f"[{100 * c['diff_ci'][0]:+.0f}, {100 * c['diff_ci'][1]:+.0f}]",
                            f"{c['a_only']} vs {c['b_only']}", _p(c["p"]), _p(c["p_holm"])]
                           for c in found if c["arm"] == arm])
            out.append("")
    return "\n".join(out)
