"""The final report: prose written by hand, every number filled in from result files.

A template names each number it needs, as {{run_set.guard.metric}} for a guard's summary in one run set, or
{{run_set.guard.subset.field}} for that run set paired against the first one (the reference) on the same guard and
scenarios, or {{run_set.guard.vs_none.field}} for a guard paired against no guard on relevant changes inside one
run set. Rendering fails on a name the results don't provide, so a typo can't leave a number blank or stale.
"""
import re
from pathlib import Path
from typing import Dict, List

from ..metrics.stats import compare, holm, pair
from .build import _p, _pct
from .contrasts import SUBSETS, load_runs
from .loops import loop_rows
from .recovery import recovery_rows
from .tables import guard_summary

SUMMARY = ("relevant_n", "relevant_fired", "relevant_success", "relevant_stale", "harmless_n", "harmless_success", "false_alarm")


def values(root, run_sets: List[str], n_boot: int = 10000, seed: int = 0) -> Dict[str, str]:
    """Named values for a template. run_sets[0] is the reference that the other run sets are paired against."""
    rows = {name: load_runs(Path(root) / name) for name in run_sets if (Path(root) / name).is_dir()}
    out = {}
    for name, rs in rows.items():
        out[f"{name}.episodes"] = str(len(rs))
        for g in guard_summary(rs):
            for m in SUMMARY:
                x = g[m]
                out[f"{name}.{g['guard']}.{m}"] = str(x) if m.endswith("_n") else _pct(x)
            out[f"{name}.{g['guard']}.calls"] = f"{g['calls']:.1f}"
        loops = loop_rows(Path(root) / name)
        for guard in dict.fromkeys(r["guard"] for r in loops):
            rs = [r for r in loops if r["guard"] == guard]
            nc = [r for r in rs if r["outcome"] == "no_commit"]
            out[f"{name}.{guard}.click_loop"] = _pct(sum(r["loop"] for r in rs) / len(rs))
            out[f"{name}.{guard}.loop_among_no_commit"] = _pct(sum(r["loop"] for r in nc) / len(nc)) if nc else "n/a"
        harmless = recovery_rows(Path(root) / name)
        for guard in dict.fromkeys(r["guard"] for r in harmless):
            rs = [r for r in harmless if r["guard"] == guard]
            missed = [r for r in rs if r["missed"]]
            out[f"{name}.{guard}.first_open_missed"] = _pct(len(missed) / len(rs))
            for key, outcome in (("recovered", "success"), ("wrong_after_miss", "wrong_item")):
                out[f"{name}.{guard}.{key}"] = (_pct(sum(r["outcome"] == outcome for r in missed) / len(missed))
                                                if missed else "n/a")
    base = run_sets[0]
    found = []
    for name, rs in rows.items():
        if name == base or base not in rows:
            continue
        for guard in dict.fromkeys(r["guard"] for r in rs):
            for subset, keep in SUBSETS.items():
                a = [r for r in rs if r["guard"] == guard and keep(r)]
                b = [r for r in rows[base] if r["guard"] == guard and keep(r)]
                if pair(a, b)[0]:
                    found.append((f"{name}.{guard}.{subset}", compare(a, b, n_boot=n_boot, seed=seed)))
    _put(out, found)
    against_none = []
    for name, rs in rows.items():
        rel = [r for r in rs if r["change_kind"] == "relevant"]
        for guard in dict.fromkeys(r["guard"] for r in rel):
            a, b = [r for r in rel if r["guard"] == guard], [r for r in rel if r["guard"] == "none"]
            if guard != "none" and pair(a, b)[0]:
                against_none.append((f"{name}.{guard}.vs_none", compare(a, b, n_boot=n_boot, seed=seed)))
    _put(out, against_none)
    return out


def _put(out: Dict[str, str], found) -> None:
    """Fields of each paired comparison, with Holm-adjusted p over the whole family passed in."""
    for (key, c), p_holm in zip(found, holm([c["p"] for _, c in found])):
        lo, hi = c["diff_ci"]
        out.update({f"{key}.pairs": str(c["n"]), f"{key}.rate": _pct(c["a_rate"]), f"{key}.base_rate": _pct(c["b_rate"]),
                    f"{key}.diff": f"{100 * c['diff']:+.0f} pts", f"{key}.ci": f"[{100 * lo:+.0f}, {100 * hi:+.0f}]",
                    f"{key}.p": _p(c["p"]), f"{key}.p_holm": _p(p_holm)})


def render(template: str, vals: Dict[str, str]) -> str:
    def fill(m):
        name = m.group(1).strip()
        if name not in vals:
            raise KeyError(f"no result for {name}")
        return vals[name]
    return re.sub(r"\{\{([^}]+)\}\}", fill, template)
