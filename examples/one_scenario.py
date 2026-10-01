"""One scenario end to end, with no GPU: generate it, run it in the live shop under two guards, score both.

The planner and executor here are scripted stand-ins for the vision models. The planner names the product it
sees on screen; the executor clicks whatever product the subtask names, then Add to cart. That is exactly the
behaviour that goes stale: under the `after_handoff` timing a cheaper product arrives after the planner has
written its subtask, and only a guard that makes the planner look again recovers.

    python examples/one_scenario.py            # needs Chrome and a built apps/dist (cd apps && npm run build)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stalehand.agents.hierarchical import Hierarchical  # noqa: E402
from stalehand.env.browser import BrowserEnv  # noqa: E402
from stalehand.guards import registry as guards  # noqa: E402
from stalehand.metrics.outcome import score  # noqa: E402
from stalehand.scenarios.domains import shop  # noqa: E402
from stalehand.scenarios.serialize import scenario_to_dict  # noqa: E402


class SeeingEnv(BrowserEnv):
    """BrowserEnv that remembers the last step whose changes reached the page, so the scripted planner can read
    the screen the way a model would."""

    def reset(self, scenario):
        self.seen_step = -1
        return super().reset(scenario)

    def _apply_due_changes(self):
        landed = super()._apply_due_changes()
        if landed:
            self.seen_step = self.step
        return landed


class Planner:
    """Writes "Add the <product> to the cart." for the product the task picks on the current screen."""
    name = "scripted-planner"

    def __init__(self, env, scenario):
        self.env, self.scenario = env, scenario

    def generate(self, requests):
        out = []
        for r in requests:
            if "Finished subtasks: none" not in r.prompt:
                out.append("Subtask: DONE")
                continue
            items = {it.id: it for it in self.scenario.items_at(self.env.seen_step)}
            target = items[self.scenario.target_at(self.env.seen_step)]
            out.append(f"Subtask: Add the {target.get('name')} to the cart.")
        return out


class Executor:
    """Follows the subtask to the letter: clicks the product it names, then Add to cart, then reports done."""
    name = "scripted-executor"

    def __init__(self, env, scenario):
        self.env, self.scenario = env, scenario

    def _click(self, box):
        x, y, w, h = box
        return f"Action: click(start_box='({int(x + w / 2)},{int(y + h / 2)})')"

    def generate(self, requests):
        out = []
        for r in requests:
            view = self.env.view()["name"]
            if view == "added":
                out.append("Action: finished(content='added')")
            elif view == "product":
                out.append(self._click(self.env.role_box("add-to-cart")))
            else:
                named = [it.id for it in self.scenario.items_at(self.scenario.last_change_step)
                         if f"Add the {it.get('name')} to" in r.prompt]
                out.append(self._click(self.env.item_boxes()[named[0]]))
        return out


def main():
    # 1. Generate: a "cheapest" shop task whose change (L1) slips a cheaper product in above the old cheapest.
    s = shop.build(seed=0, kind="cheapest", index=0, variant="L1", change_step=0)
    names = {it.id: it.get("name") for it in s.items_at(s.last_change_step)}
    print("task:          ", s.task)
    print("change kind:   ", s.change_kind)
    print("planner sees:  ", s.stale_target, names[s.stale_target])
    print("correct after: ", s.target_at(s.last_change_step), names[s.target_at(s.last_change_step)])
    print("scenario JSON: ", len(json.dumps(scenario_to_dict(s))), "bytes, as `stalehand scenarios` writes it")

    # 2. Run it under no guard and under re-planning every step, then 3. score each episode.
    env = SeeingEnv(change_timing="after_handoff")
    try:
        for guard in ("none", "replan_every_step"):
            agent = Hierarchical(Planner(env, s), Executor(env, s), guards.make(guard), max_steps=6)
            traj = agent.run(env, s)
            row = score(s, traj)
            subtasks = [e["text"] for e in traj.entries if e["kind"] == "subtask"]
            print(f"\n[{guard}]")
            print("  subtasks:      ", subtasks)
            print("  added to cart: ", row["target"], names.get(row["target"]))
            print("  outcome:       ", row["outcome"], f"(planner calls {row['planner_calls']})")
    finally:
        env.close()


if __name__ == "__main__":
    main()
