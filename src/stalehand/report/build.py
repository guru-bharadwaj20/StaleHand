"""Markdown report of a set of runs: outcome rates per group, and paired guard comparisons against a baseline."""
from typing import List

from ..metrics.stats import compare, pair
from .tables import guard_summary, rates

COLUMNS = ("success", "stale", "wrong_item", "wrong_detail", "aborted", "no_commit")


def domain_of(row: dict) -> str:
    return row["scenario_id"].split("-", 1)[0]


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.0f}%"


def _table(header: List[str], lines: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return out + ["| " + " | ".join(line) + " |" for line in lines]


def markdown(rows: List[dict], baseline: str = "none", n_boot: int = 10000, seed: int = 0) -> str:
    rows = [dict(r, domain=domain_of(r)) for r in rows]
    out = [f"Built from {len(rows)} scored episodes.", "", "## Summary by guard", "",
           "Relevant: the change moved or removed the target the planner saw. Harmless: no change, or one that "
           "leaves the target where it was. Calls: planner plus checker calls per episode.", ""]
    out += _table(["architecture", "guard", "relevant n", "success", "stale", "harmless n", "success",
                   "false alarms", "calls"],
                  [[g["architecture"], g["guard"], str(g["relevant_n"]), _pct(g["relevant_success"]),
                    _pct(g["relevant_stale"]), str(g["harmless_n"]), _pct(g["harmless_success"]),
                    _pct(g["false_alarm"]), f"{g['calls']:.1f}"] for g in guard_summary(rows)])
    out += ["", "## Outcomes", ""]
    groups = rates(rows, by=("architecture", "guard", "domain", "kind", "change_kind"))
    out += _table(["architecture", "guard", "domain", "kind", "change", "n", *COLUMNS, "planner calls"],
                  [[g["architecture"], g["guard"], g["domain"], str(g["kind"]), g["change_kind"], str(g["n"]),
                    *[_pct(g[f"{c}_rate"]) for c in COLUMNS], f"{g['planner_calls']:.1f}"] for g in groups])

    out += ["", "## False alarms on harmless changes", ""]
    fa = rates(rows, by=("architecture", "guard"))
    out += _table(["architecture", "guard", "episodes", "false alarm rate", "planner calls"],
                  [[g["architecture"], g["guard"], str(g["n"]), _pct(g["false_alarm_rate"]),
                    f"{g['planner_calls']:.1f}"] for g in fa])

    out += ["", f"## Paired against `{baseline}` on relevant changes", "",
            "Same scenarios in both arms. Difference is the guard's success rate minus the baseline's, with a "
            f"95% bootstrap interval over scenario templates ({n_boot} resamples, seed {seed}) and an exact "
            "McNemar test on the discordant pairs.", ""]
    lines = []
    relevant = [r for r in rows if r["change_kind"] == "relevant"]
    for arch in dict.fromkeys(r["architecture"] for r in relevant):
        arms = [r for r in relevant if r["architecture"] == arch]
        guards = [g for g in dict.fromkeys(r["guard"] for r in arms) if g != baseline]
        for guard in guards:
            for dom in [*dict.fromkeys(r["domain"] for r in arms), "all"]:
                pick = lambda g: [r for r in arms if r["guard"] == g and (dom == "all" or r["domain"] == dom)]
                base, other = pick(baseline), pick(guard)
                if not base or not other:
                    continue
                if not pair(other, base)[0]:  # partial runs: the two arms have not reached the same scenarios
                    lines.append([arch, guard, dom, "0", "no shared scenarios yet", "", "", "", "", ""])
                    continue
                c = compare(other, base, n_boot=n_boot, seed=seed)
                lo, hi = c["diff_ci"]
                lines.append([arch, guard, dom, str(c["n"]), _pct(c["b_rate"]), _pct(c["a_rate"]),
                              f"{100 * c['diff']:+.0f} pts", f"[{100 * lo:+.0f}, {100 * hi:+.0f}]",
                              f"{c['a_only']} vs {c['b_only']}", f"p = {c['p']:.3f}"])
    out += _table(["architecture", "guard", "domain", "pairs", baseline, "guard", "difference", "95% CI",
                   "only guard vs only baseline succeeded", "McNemar"], lines)
    return "\n".join(out) + "\n"
