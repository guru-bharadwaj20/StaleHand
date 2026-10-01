"""Block or re-plan when the page's DOM changed for reasons other than the agent's own actions.

scope="step" is the time-of-check/time-of-use defence of arXiv 2603.00476: it watches only the window between
the executor's screenshot and its action. scope="subtask" watches everything since the subtask was written.
The original defence aborts; on_change="replan" asks the planner again instead.
"""
from .base import ABORT, PROCEED, REPLAN, Context, Guard


class DomChange(Guard):
    def __init__(self, scope: str = "step", on_change: str = "abort"):
        if scope not in ("step", "subtask") or on_change not in ("abort", "replan"):
            raise ValueError("scope must be step or subtask; on_change must be abort or replan")
        self.scope, self.on_change = scope, on_change
        self.name = f"dom_{scope}_{on_change}"

    def _verdict(self, ctx: Context) -> str:
        if ctx.env.external_since_mark() == 0:
            return PROCEED
        return ABORT if self.on_change == "abort" else REPLAN

    def on_subtask(self, ctx: Context) -> None:
        if self.scope == "subtask":
            ctx.env.mark_external()

    def before_think(self, ctx: Context) -> str:
        if self.scope == "step":
            ctx.env.mark_external()
            return PROCEED
        return self._verdict(ctx)

    def before_act(self, ctx: Context) -> str:
        return self._verdict(ctx) if self.scope == "step" else PROCEED
