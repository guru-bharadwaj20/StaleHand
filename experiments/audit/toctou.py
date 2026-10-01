"""Model-free measure of the time-of-check/time-of-use hazard: a click aimed from the screenshot, landing after the
page changed.

For each scenario, under the mid_step timing with the change at step 0: read where the target the planner saw sits
on the screenshot, let the change land (as it does between the executor's screenshot and its action), click the old
position, and record which item the click opened. Rows say whether the click still hit the intended item, hit the
item that is now correct, hit another item, or hit nothing.

usage: python toctou.py --domain inbox --n 10 --out toctou_inbox.jsonl [--channel none]
"""
import argparse
import json
import os

from stalehand.env.actions import Click
from stalehand.env.browser import BrowserEnv
from stalehand.scenarios import registry


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--domain", required=True, choices=sorted(registry.DOMAINS))
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--channel", default=os.environ.get("STALEHAND_CHANNEL", "chrome"))
    a = p.parse_args()
    env = BrowserEnv(change_timing="mid_step", channel=None if a.channel == "none" else a.channel)
    try:
        with open(a.out, "w") as f:
            for s in registry.generate(a.domain, seed=a.seed, n=a.n, change_step=0):
                env.reset(s)
                box = env.item_boxes().get(s.stale_target)
                if box is None:
                    continue
                x, y, w, h = box
                env.begin_action()  # the change lands between the screenshot and the click
                env.act(Click(int(x + w / 2), int(y + h / 2)))
                opened = [e.get("itemId") for e in env.events() if e.get("step") == 0 and e.get("itemId")]
                hit = opened[0] if opened else None
                final = s.target_at(s.last_change_step)
                verdict = ("intended" if hit == s.stale_target else "now_correct" if hit is not None and hit == final
                           else "nothing" if hit is None else "other_item")
                f.write(json.dumps({"scenario_id": s.id, "domain": a.domain, "kind": s.meta.get("kind"),
                                    "variant": s.meta.get("variant"), "change_kind": s.change_kind,
                                    "clicked": hit, "verdict": verdict}, sort_keys=True) + "\n")
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
