"""Stall audit: would the stall return (hierarchical_stall) cut off a correct run?

The stall return hands control back to the planner after two actions in a row that leave the screenshot
byte-identical. For each scenario, the oracle from oracle.py performs the correct committing flow under the
after_handoff timing, and this records which of its actions left the screen unchanged. A scenario whose correct flow
has two unchanged actions in a row would be interrupted by the stall return even when the executor does everything
right.

usage: python stall.py --domain files --n 10 --out stall_files.jsonl [--channel none]
"""
import argparse
import json
import os

from oracle import centre, flow

from stalehand.env.actions import Type
from stalehand.env.browser import BrowserEnv
from stalehand.scenarios import registry


def correct_flow(env, scenario, target):
    """Unchanged flags for each oracle action, or None when the target is not on screen."""
    env.reset(scenario)
    env.handoff()
    boxes = env.item_boxes()
    if target not in boxes:
        return None
    before, flags = env.observe().png, []

    def act(action):
        nonlocal before
        after = env.act(action).png
        flags.append(after == before)
        before = after

    act(centre(boxes[target]))
    for step in flow(scenario):
        if isinstance(step, tuple):
            act(Type(step[1]))
            continue
        box = env.role_box(step)
        if box is None:
            return flags
        act(centre(box))
    return flags


def longest_run(flags):
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


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
                flags = correct_flow(env, s, final) if final is not None else None
                row = {"scenario_id": s.id, "domain": a.domain, "change_kind": s.change_kind, "unchanged": flags,
                       "longest_unchanged_run": None if flags is None else longest_run(flags)}
                f.write(json.dumps(row, sort_keys=True) + "\n")
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
