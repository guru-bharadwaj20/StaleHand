"""Recovery after a missed first click, on harmless changes.

When a change lands between the executor's screenshot and its click (mid_step), the click often opens another item
even though the change didn't matter to the task. What happens next depends on the guard: a guard that checks before
the click can stop it, and one that checks only before the next thought re-plans from the wrong item's screen.
"""
import json
from pathlib import Path
from typing import List, Optional

from .build import _pct, _table
from .tables import HARMLESS


def first_open_missed(traj: dict, correct: str) -> Optional[bool]:
    """Whether the first item the agent opened was not the correct one; None when it opened nothing."""
    first = next((e for e in traj.get("app_events", []) if e.get("kind") == "open"), None)
    return None if first is None else first.get("itemId") != correct


def recovery_rows(run_set) -> List[dict]:
    """One row per harmless-change episode under a run-set directory."""
    root, out = Path(run_set), []
    for path in sorted(root.rglob("results.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            t = path.parent / "trajectories" / f"{r['scenario_id']}.json"
            if r["change_kind"] not in HARMLESS or not t.exists():
                continue
            out.append({"run_set": root.name, "architecture": r["architecture"], "guard": r["guard"],
                        "outcome": r["outcome"],
                        "missed": first_open_missed(json.loads(t.read_text()), r["correct_target"])})
    return out


def markdown(rows: List[dict]) -> str:
    groups = {}
    for r in rows:
        groups.setdefault((r["run_set"], r["architecture"], r["guard"]), []).append(r)
    lines = []
    for key, rs in groups.items():
        missed = [r for r in rs if r["missed"]]
        share = lambda o: _pct(sum(r["outcome"] == o for r in missed) / len(missed)) if missed else "n/a"
        lines.append([*key, str(len(rs)), _pct(len(missed) / len(rs)), share("success"), share("wrong_item")])
    head = [f"Built from {len(rows)} episodes with a harmless change. Missed: the first item the agent opened was "
            "not the correct one. The last two columns are over the missed episodes only.", ""]
    return "\n".join(head + _table(["run set", "architecture", "guard", "episodes", "first open missed",
                                    "then succeeded", "then committed to a wrong item"], lines)) + "\n"


if __name__ == "__main__":
    import sys
    print(markdown([r for d in sys.argv[1:] for r in recovery_rows(d)]), end="")
