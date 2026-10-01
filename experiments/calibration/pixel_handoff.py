"""How much does the screen change at the handoff, for harmless and for relevant changes?

For every scenario: load it, screenshot what the planner sees, apply the step-0 changes the way the after_handoff
timing does, screenshot what the executor sees, and measure both the pixel difference (crates/screendiff) and the DOM
mutations the change caused. No model is involved, so this runs on any machine with a browser (worker3 does it).

usage: python pixel_handoff.py --domain inbox --n 10 --out pixel_inbox.jsonl [--channel none]
"""
import argparse
import json
import os

from stalehand.env.browser import BrowserEnv
from stalehand.guards import screendiff
from stalehand.scenarios import registry


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--domain", required=True, choices=sorted(registry.DOMAINS))
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--channel", default=os.environ.get("STALEHAND_CHANNEL", "chrome"),
                   help='"chrome" for the system browser, "none" for Playwright\'s own Chromium')
    a = p.parse_args()
    env = BrowserEnv(change_timing="after_handoff", channel=None if a.channel == "none" else a.channel)
    try:
        with open(a.out, "w") as f:
            for s in registry.generate(a.domain, seed=a.seed, n=a.n, change_step=0):
                before = env.reset(s).png
                env.mark_external()
                changed = env.handoff()
                after = env.observe().png
                diff = screendiff.compare(before, after)
                f.write(json.dumps({"scenario_id": s.id, "domain": a.domain, "kind": s.meta.get("kind"),
                                    "variant": s.meta.get("variant"), "change_kind": s.change_kind,
                                    "landed": changed, "dom_mutations": env.external_since_mark(),
                                    "changed_fraction": diff["changed_fraction"], "ssim": diff["ssim"]},
                                   sort_keys=True) + "\n")
    finally:
        env.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
