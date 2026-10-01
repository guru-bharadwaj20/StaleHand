"""Click loops: episodes that hit the step limit while the executor kept clicking one spot.

In the main runs most no-commit episodes end this way: the executor's click worked, the screen moved on, and it
kept clicking a label that looks like the button it was told to press, never handing control back.
"""
import json
from pathlib import Path
from typing import List

from .build import _pct, _table


def click_loop(traj: dict, repeat: int = 4, radius: int = 15) -> bool:
    """The episode hit the step limit and its last `repeat` actions were clicks within `radius` px of the last."""
    if traj.get("end_reason") != "max_steps":
        return False
    acts = [e["action"] for e in traj["entries"] if e["kind"] == "action"][-repeat:]
    if len(acts) < repeat or any(a is None or a["type"] != "click" for a in acts):
        return False
    x, y = acts[-1]["x"], acts[-1]["y"]
    return all(abs(a["x"] - x) <= radius and abs(a["y"] - y) <= radius for a in acts)


def loop_rows(run_set) -> List[dict]:
    """One row per episode under a run-set directory: its outcome, how it ended, and whether it was a click loop."""
    root, rows = Path(run_set), []
    for path in sorted(root.rglob("results.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            t = path.parent / "trajectories" / f"{r['scenario_id']}.json"
            traj = json.loads(t.read_text()) if t.exists() else {"entries": []}
            rows.append({"run_set": root.name, "architecture": r["architecture"], "guard": r["guard"],
                         "outcome": r["outcome"], "end_reason": traj.get("end_reason"), "loop": click_loop(traj)})
    return rows


def markdown(rows: List[dict]) -> str:
    groups = {}
    for r in rows:
        groups.setdefault((r["run_set"], r["architecture"], r["guard"]), []).append(r)
    frac = lambda rs, f: sum(map(f, rs)) / len(rs)
    lines = [[*key, str(len(rs)), _pct(frac(rs, lambda r: r["outcome"] == "no_commit")),
              _pct(frac(rs, lambda r: r["end_reason"] == "max_steps")), _pct(frac(rs, lambda r: r["loop"])),
              _pct(frac(nc, lambda r: r["loop"])) if (nc := [r for r in rs if r["outcome"] == "no_commit"]) else "n/a"]
             for key, rs in groups.items()]
    head = [f"Built from {len(rows)} episodes. Click loop: the episode hit the step limit and its last four actions "
            "were clicks within 15 px of one spot.", ""]
    return "\n".join(head + _table(["run set", "architecture", "guard", "episodes", "no commit", "ran out of steps",
                                    "click loop", "click loop among no commit"], lines)) + "\n"


if __name__ == "__main__":
    import sys
    print(markdown([r for d in sys.argv[1:] for r in loop_rows(d)]), end="")
