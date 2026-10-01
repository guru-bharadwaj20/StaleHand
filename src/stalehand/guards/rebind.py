"""Rebind: keep the planner's rule next to the concrete target it picked, and re-resolve the rule on the live
screen. If the rule now picks a different element, swap that element into the subtask without calling the planner
again; if it picks nothing, re-plan.

trigger="step" re-resolves on every new screen; trigger="dom" only after the page changed for reasons other than
the agent's own actions, so harmless screens cost no model call.
"""
import time

from ..models import prompts
from ..models.base import Request
from ..models.text_parsers import parse_target, same_target
from .base import PROCEED, REBIND, REPLAN, Context, Guard


class Rebind(Guard):
    planner_mode = "bound"

    def __init__(self, resolver, trigger: str = "step", max_new_tokens: int = 48):
        if trigger not in ("step", "dom"):
            raise ValueError("trigger must be step or dom")
        self.resolver, self.trigger, self.max_new_tokens = resolver, trigger, max_new_tokens
        self.name = f"rebind_{trigger}"

    def on_subtask(self, ctx: Context) -> None:
        if self.trigger == "dom":
            ctx.env.mark_external()

    def _resolve(self, ctx: Context):
        req = Request(prompts.RESOLVE.format(rule=ctx.extra["rule"]), ctx.png, self.max_new_tokens)
        t0 = time.perf_counter()
        out = self.resolver.generate([req])[0]
        target = parse_target(out)
        if ctx.trajectory is not None:
            ctx.trajectory.model_call(step=ctx.step, role="checker", model=self.resolver.name, output=out,
                                      seconds=time.perf_counter() - t0, resolved=target)
        return out, target

    def before_think(self, ctx: Context) -> str:
        if ctx.on_planning_screen() or "rule" not in ctx.extra:
            return PROCEED
        if self.trigger == "dom":
            if ctx.env.external_since_mark() == 0:
                return PROCEED
            ctx.env.mark_external()
        out, target = self._resolve(ctx)
        if target is None:
            return REPLAN if "Target:" in out else PROCEED
        if same_target(target, ctx.extra["target"]):
            return PROCEED
        ctx.extra["target"] = target
        ctx.subtask = f"{ctx.extra['action']} - {target}"
        return REBIND
