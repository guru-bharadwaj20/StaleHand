"""Outcome rates per group of result rows."""
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

OUTCOMES = ("success", "stale", "wrong_item", "wrong_detail", "aborted", "no_commit")
HARMLESS = ("none", "irrelevant")


def load_rows(root) -> List[dict]:
    """Every row of every results.jsonl under root, in path order."""
    rows = []
    for path in sorted(Path(root).rglob("results.jsonl")):
        rows += [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return rows


def rates(rows: Iterable[dict], by: Sequence[str]) -> List[Dict]:
    """One dict per group (first-seen order): counts and rates of each outcome, false alarms, planner calls.

    The false-alarm rate is over episodes whose change was harmless (none or irrelevant), the only ones where a
    guard firing is always unwarranted; it is None when a group has no such episode.
    """
    groups: Dict[tuple, List[dict]] = {}
    for r in rows:
        groups.setdefault(tuple(r.get(k) for k in by), []).append(r)
    out = []
    for key, rs in groups.items():
        n = len(rs)
        g = dict(zip(by, key), n=n)
        for o in OUTCOMES:
            g[o] = sum(r["outcome"] == o for r in rs)
            g[f"{o}_rate"] = g[o] / n
        harmless = [r for r in rs if r["change_kind"] in HARMLESS]
        g["harmless_n"] = len(harmless)
        g["false_alarm_rate"] = sum(r["false_alarm"] for r in harmless) / len(harmless) if harmless else None
        g["planner_calls"] = sum(r["planner_calls"] for r in rs) / n
        out.append(g)
    return out


def guard_summary(rows: Iterable[dict]) -> List[Dict]:
    """One line per (architecture, guard): what happens on relevant changes, on harmless ones, and the model-call
    cost (planner plus checker calls per episode). target_removed episodes are left out of both halves."""
    out = []
    for g in rates(rows, by=("architecture", "guard")):
        rs = [r for r in rows if r["architecture"] == g["architecture"] and r["guard"] == g["guard"]]
        rel = [r for r in rs if r["change_kind"] == "relevant"]
        harm = [r for r in rs if r["change_kind"] in HARMLESS]
        frac = lambda xs, f: sum(map(f, xs)) / len(xs) if xs else None
        out.append({"architecture": g["architecture"], "guard": g["guard"], "n": g["n"],
                    "relevant_n": len(rel), "relevant_success": frac(rel, lambda r: r["outcome"] == "success"),
                    "relevant_stale": frac(rel, lambda r: r["outcome"] == "stale"),
                    "relevant_fired": frac(rel, lambda r: r.get("fired", 0) > 0),
                    "harmless_n": len(harm), "harmless_success": frac(harm, lambda r: r["outcome"] == "success"),
                    "false_alarm": frac(harm, lambda r: r["false_alarm"]),
                    "calls": sum(r["planner_calls"] + r.get("checker_calls", 0) for r in rs) / len(rs)})
    return out
