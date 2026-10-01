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
        g["false_alarm_rate"] = sum(r["false_alarm"] for r in harmless) / len(harmless) if harmless else None
        g["planner_calls"] = sum(r["planner_calls"] for r in rs) / n
        out.append(g)
    return out
