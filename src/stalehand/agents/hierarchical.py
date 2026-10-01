"""Planner and executor (Agent S2 style): the planner writes a subtask from the screen it sees; the executor
works through it, one action per step, until it reports finished(); then the planner writes the next one.

Guards hook in before the executor thinks and before it acts (see guards/base.py).
"""
import time
from typing import Optional, Tuple

from ..env.actions import Done, Wait
from ..env.browser import VIEWPORT
from ..guards.base import ABORT, REPLAN, Context, Guard
from ..models import prompts
from ..models.base import Request
from ..models.text_parsers import parse_bound, parse_rule, parse_subtask
from ..models.uitars import parse_action
from .trajectory import Trajectory


class Hierarchical:
    architecture = "hierarchical"

    def __init__(self, planner, executor, guard: Guard, max_steps: int = 12, max_replans: int = 3,
                 executor_coords: str = "abs", planner_tokens: int = 160, executor_tokens: int = 256):
        self.planner, self.executor, self.guard = planner, executor, guard
        self.max_steps, self.max_replans, self.coords = max_steps, max_replans, executor_coords
        self.planner_tokens, self.executor_tokens = planner_tokens, executor_tokens

    def _call(self, model, role: str, req: Request, step: int, traj: Trajectory) -> str:
        t0 = time.perf_counter()
        out = model.generate([req])[0]
        traj.model_call(step=step, role=role, model=model.name, output=out, seconds=time.perf_counter() - t0)
        return out

    def _plan(self, task: str, finished, png: bytes, step: int, traj: Trajectory) -> Optional[Tuple[str, dict]]:
        """(subtask, extra fields for the guard), or None when the planner says the task is done."""
        history = "; ".join(finished) if finished else "none"
        mode = self.guard.planner_mode
        template = {"rule": prompts.RULE_PLANNER, "bound": prompts.BOUND_PLANNER}.get(mode, prompts.PLANNER)
        out = self._call(self.planner, "planner", Request(template.format(task=task, history=history), png,
                                                          self.planner_tokens), step, traj)
        if mode == "rule":
            parsed = parse_rule(out)
            return None if parsed is None else (parsed[0], {"rule": parsed[1]})
        if mode == "bound":
            parsed = parse_bound(out)
            return None if parsed is None else (parsed[0], dict(zip(("rule", "target", "action"), parsed[1:])))
        text = parse_subtask(out)
        return None if text is None else (text, {})

    def run(self, env, scenario) -> Trajectory:
        traj = Trajectory(scenario.id, self.architecture, self.guard.name)
        obs = env.reset(scenario)
        finished, replans = [], {}  # replans per env step; only repeated re-planning without acting is bounded

        def new_subtask(o) -> Optional[Context]:
            planned = self._plan(scenario.task, finished, o.png, o.step, traj)
            if planned is None:
                return None
            text, extra = planned
            traj.subtask(step=o.step, text=text, **extra)
            c = Context(env=env, task=scenario.task, subtask=text, subtask_step=o.step, subtask_png=o.png,
                        step=o.step, png=o.png, trajectory=traj, extra=extra)
            self.guard.on_subtask(c)
            return c

        ctx = new_subtask(obs)
        history = []
        while ctx is not None:
            if env.step >= self.max_steps:
                return self._end(traj, env, "max_steps")
            ctx.step, ctx.png, ctx.action = obs.step, obs.png, None
            decision = self.guard.before_think(ctx)
            traj.decision(step=obs.step, guard=self.guard.name, decision=decision, moment="think")
            if decision == ABORT:
                return self._end(traj, env, "guard_abort")
            if decision == REPLAN:
                replans[obs.step] = replans.get(obs.step, 0) + 1
                if replans[obs.step] > self.max_replans:
                    return self._end(traj, env, "max_replans")
                ctx, history = new_subtask(obs), []
                continue
            req = Request(prompts.EXECUTOR.format(instruction=ctx.subtask,
                                                  history="\n".join(history) if history else "none"),
                          obs.png, self.executor_tokens)
            raw = self._call(self.executor, "executor", req, obs.step, traj)
            action = parse_action(raw, VIEWPORT, self.coords)
            if isinstance(action, Done):
                traj.action(step=obs.step, action=action, raw=raw)
                finished.append(ctx.subtask)
                ctx, history = new_subtask(obs), []
                continue
            env.begin_action()
            ctx.action = action
            decision = self.guard.before_act(ctx)
            traj.decision(step=obs.step, guard=self.guard.name, decision=decision, moment="act")
            if decision == ABORT:
                return self._end(traj, env, "guard_abort")
            if decision == REPLAN:
                replans[obs.step] = replans.get(obs.step, 0) + 1
                if replans[obs.step] > self.max_replans:
                    return self._end(traj, env, "max_replans")
                obs = env.observe()
                ctx, history = new_subtask(obs), []
                continue
            traj.action(step=obs.step, action=action, raw=raw)
            obs = env.act(action if action is not None else Wait())
            history.append(f"{len(history) + 1}. {raw.strip().splitlines()[-1] if raw.strip() else 'none'}")
        return self._end(traj, env, "planner_done")

    @staticmethod
    def _end(traj: Trajectory, env, reason: str) -> Trajectory:
        traj.finish(reason=reason, app_events=env.events())
        return traj
