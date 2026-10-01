"""Oracle audit: can every scenario be solved, and does the scorer agree with ground truth?

For each scenario, under the after_handoff timing (the main comparison's), an oracle that reads item positions from
the page performs the domain's committing flow twice: once on the correct target (the scenario's target after its
changes) and once on the stale target (the one the planner saw). Expected scores: success for the correct target
(unless the change removed it), and stale for the stale target whenever the two differ. Any other score, or a target
that is not on screen when the data says it should be, points at a broken scenario, app or scorer, before models
are spent on it. A stale target that the change removed (sold out, deleted) is expected to be off screen.

usage: python oracle.py --domain files --n 10 --out oracle_files.jsonl [--channel none]
"""
import argparse
import json
import os

from stalehand.agents.trajectory import Trajectory
from stalehand.env.actions import Click, Type
from stalehand.env.browser import BrowserEnv
from stalehand.metrics.outcome import score
from stalehand.scenarios import registry


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def flow(scenario):
    """The roles to click (and text to type) after opening the item, per domain and action."""
    action, to = scenario.meta.get("action"), scenario.meta.get("recipient")
    return {
        "open": [],
        "forward": ["forward", "to", ("type", to), "send"],
        "reply": ["reply", "body", ("type", "Thanks, noted."), "send"],
        "add_to_cart": ["add-to-cart"],
        "share": ["share", "to", ("type", to), "send"],
        "assign": ["assign", "to", ("type", to), "save"],
        "join": ["join"],
    }[action] if scenario.domain != "chat" else ["body", ("type", "Thanks, noted."), "send"]


def attempt(env, scenario, target):
    env.reset(scenario)
    env.handoff()
    boxes = env.item_boxes()
    if target is None or target not in boxes:
        return {"result": "not_on_screen"}
    env.act(centre(boxes[target]))
    for step in flow(scenario):
        if isinstance(step, tuple):
            env.act(Type(step[1]))
            continue
        box = env.role_box(step)
        if box is None:
            return {"result": f"no_{step}_control"}
        env.act(centre(box))
    t = Trajectory(scenario.id, "oracle", "none")
    t.finish("oracle_done", env.events())
    return {"result": score(scenario, t)["outcome"]}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--domain", required=True, choices=sorted(registry.DOMAINS))
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--channel", default=os.environ.get("STALEHAND_CHANNEL", "chrome"))
    a = p.parse_args()
    env = BrowserEnv(change_timing="after_handoff", channel=None if a.channel == "none" else a.channel)
    try:
        with open(a.out, "w") as f:
            for s in registry.generate(a.domain, seed=a.seed, n=a.n, change_step=0):
                final = s.target_at(s.last_change_step)
                row = {"scenario_id": s.id, "domain": a.domain, "kind": s.meta.get("kind"),
                       "variant": s.meta.get("variant"), "change_kind": s.change_kind,
                       "correct": attempt(env, s, final)["result"] if final is not None else "removed",
                       "stale": attempt(env, s, s.stale_target)["result"]}
                row["expected_correct"] = "success" if final is not None else "removed"
                still_listed = s.stale_target in {it.id for it in s.items_at(s.last_change_step)}
                row["expected_stale"] = ("success" if s.stale_target == final else
                                         "stale" if still_listed else "not_on_screen")
                row["ok"] = row["correct"] == row["expected_correct"] and row["stale"] == row["expected_stale"]
                f.write(json.dumps(row, sort_keys=True) + "\n")
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
