"""Markdown report of a set of runs: outcome rates per group, and paired guard comparisons against a baseline."""
from typing import List

from ..metrics.stats import compare, pair
from .tables import guard_summary, rates

COLUMNS = ("success", "stale", "wrong_item", "wrong_detail", "aborted", "no_commit")


def domain_of(row: dict) -> str:
    return row["scenario_id"].split("-", 1)[0]


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.0f}%"


def _p(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def _by_guard(rows: List[dict]) -> dict:
    groups = {}
    for r in rows:
        groups.setdefault((r["architecture"], r["guard"]), []).append(r)
    return groups


def _share(rows: List[dict], change_kind: str, ok) -> str:
    rs = [r for r in rows if r["change_kind"] == change_kind]
    return f"{_pct(sum(map(ok, rs)) / len(rs))} of {len(rs)}" if rs else "n/a"


def _table(header: List[str], lines: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return out + ["| " + " | ".join(line) + " |" for line in lines]


def markdown(rows: List[dict], baseline: str = "none", n_boot: int = 10000, seed: int = 0) -> str:
    rows = [dict(r, domain=domain_of(r)) for r in rows]
    out = [f"Built from {len(rows)} scored episodes.", "", "## Summary by guard", "",
           "Relevant: the change moved or removed the target the planner saw. Harmless: no change, or one that "
           "leaves the target where it was. Fired: the guard re-planned, re-bound or aborted at least once. Calls: "
           "planner plus checker calls per episode.", ""]
    out += _table(["architecture", "guard", "relevant n", "fired", "success", "stale", "harmless n", "success",
                   "false alarms", "calls"],
                  [[g["architecture"], g["guard"], str(g["relevant_n"]), _pct(g["relevant_fired"]),
                    _pct(g["relevant_success"]), _pct(g["relevant_stale"]), str(g["harmless_n"]),
                    _pct(g["harmless_success"]),
                    _pct(g["false_alarm"]), f"{g['calls']:.1f}"] for g in guard_summary(rows)])
    out += ["", "## By change kind", "",
            "Success on each kind of change. When the change removed the target there is no correct item, so the "
            "column counts episodes that held off: no commit, or a guard abort.", ""]
    out += _table(["architecture", "guard", "no change", "irrelevant", "relevant", "target removed: held off"],
                  [[arch, guard, *[_share(rs, k, lambda r: r["outcome"] == "success")
                                   for k in ("none", "irrelevant", "relevant")],
                    _share(rs, "target_removed", lambda r: r["outcome"] in ("no_commit", "aborted"))]
                   for (arch, guard), rs in _by_guard(rows).items()])
    relevant = [r for r in rows if r["change_kind"] == "relevant"]
    tasks = sorted({(r["domain"], str(r["kind"])) for r in relevant})
    if tasks:
        out += ["", "## Relevant changes by task", "", "Success on episodes whose change moved the target, per task.", ""]
        out += _table(["architecture", "guard", *[f"{d} {k}" for d, k in tasks]],
                      [[arch, guard, *[_share([r for r in rs if (r["domain"], str(r["kind"])) == t], "relevant",
                                              lambda r: r["outcome"] == "success") for t in tasks]]
                       for (arch, guard), rs in _by_guard(rows).items()])
    out += ["", "## Outcomes", ""]
    groups = sorted(rates(rows, by=("architecture", "guard", "domain", "kind", "change_kind")),
                    key=lambda g: (g["architecture"], g["guard"] != baseline, g["guard"], g["domain"],
                                   str(g["kind"]), g["change_kind"]))
    out += _table(["architecture", "guard", "domain", "kind", "change", "n", *COLUMNS, "planner calls"],
                  [[g["architecture"], g["guard"], g["domain"], str(g["kind"]), g["change_kind"], str(g["n"]),
                    *[_pct(g[f"{c}_rate"]) for c in COLUMNS], f"{g['planner_calls']:.1f}"] for g in groups])

    out += ["", "## Cost per episode", "",
            "Means per episode. Model seconds add up the latency of every model call, so they include time spent "
            "waiting in a shared server's batch; compare them within one run set only.", ""]
    mean = lambda rs, k: f"{sum(r.get(k, 0) for r in rs) / len(rs):.1f}"
    out += _table(["architecture", "guard", "planner calls", "checker calls", "executor calls", "model seconds",
                   "actions"],
                  [[arch, guard, *[mean(rs, k) for k in ("planner_calls", "checker_calls", "executor_calls",
                                                         "model_seconds", "env_steps")]]
                   for (arch, guard), rs in _by_guard(rows).items()])

    out += ["", "## False alarms on harmless changes", ""]
    fa = rates(rows, by=("architecture", "guard"))
    out += _table(["architecture", "guard", "harmless episodes", "false alarm rate", "planner calls"],
                  [[g["architecture"], g["guard"], str(g["harmless_n"]), _pct(g["false_alarm_rate"]),
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
                              f"{c['a_only']} vs {c['b_only']}", _p(c["p"])])
    out += _table(["architecture", "guard", "domain", "pairs", baseline, "guard", "difference", "95% CI",
                   "only guard vs only baseline succeeded", "McNemar"], lines)
    return "\n".join(out) + "\n"
