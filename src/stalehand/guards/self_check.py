"""Self-check: before each step on a screen the subtask was not written on, ask a model whether the subtask
still fits the screen; re-plan on STALE. In the pilot this caught 9-26% of stale subtasks."""
import time

from ..models import prompts
from ..models.base import Request
from ..models.text_parsers import parse_verdict
from .base import PROCEED, REPLAN, Context, Guard


class SelfCheck(Guard):
    name = "self_check"

    def __init__(self, checker, max_new_tokens: int = 96):
        self.checker, self.max_new_tokens = checker, max_new_tokens

    def before_think(self, ctx: Context) -> str:
        if ctx.step == ctx.subtask_step:
            return PROCEED
        req = Request(prompts.SELF_CHECK.format(task=ctx.task, subtask=ctx.subtask), ctx.png, self.max_new_tokens)
        t0 = time.perf_counter()
        out = self.checker.generate([req])[0]
        if ctx.trajectory is not None:
            ctx.trajectory.model_call(step=ctx.step, role="checker", model=self.checker.name, output=out,
                                      seconds=time.perf_counter() - t0, verdict=parse_verdict(out))
        return REPLAN if parse_verdict(out) == "STALE" else PROCEED
