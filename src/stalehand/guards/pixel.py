"""Block or re-plan when the screenshot changed too much since the subtask was written (in the spirit of the
pre-execution pixel check of arXiv 2604.18860). The agent's own actions also change pixels, which is the cost."""
from . import screendiff
from .base import ABORT, PROCEED, REPLAN, Context, Guard


class PixelChange(Guard):
    def __init__(self, threshold: float = 0.02, on_change: str = "replan"):
        if on_change not in ("abort", "replan"):
            raise ValueError("on_change must be abort or replan")
        self.threshold, self.on_change = threshold, on_change
        self.name = f"pixel_{threshold:g}_{on_change}"

    def before_think(self, ctx: Context) -> str:
        if ctx.on_planning_screen():
            return PROCEED
        report = screendiff.compare(ctx.subtask_png, ctx.png)
        if ctx.trajectory is not None:
            ctx.trajectory.decision(step=ctx.step, guard=self.name, decision="measured", diff=report)
        if report["changed_fraction"] <= self.threshold:
            return PROCEED
        return ABORT if self.on_change == "abort" else REPLAN
