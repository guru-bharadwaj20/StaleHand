"""Re-plan before every executor step: the planner always writes from the current screen. The upper bound on
freshness, at one planner call per step."""
from .base import PROCEED, REPLAN, Context, Guard


class ReplanEveryStep(Guard):
    name = "replan_every_step"

    def before_think(self, ctx: Context) -> str:
        return PROCEED if ctx.on_planning_screen() else REPLAN
