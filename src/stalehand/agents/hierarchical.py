"""Planner and executor (Agent S2 style): the planner writes a subtask from the screen it sees; the executor
works through it, one action per step, until it reports finished(); then the planner writes the next one.

Guards hook in before the executor thinks and before it acts (see guards/base.py).
"""
import time
from typing import Optional

from ..env.actions import Done, Wait
from ..env.browser import VIEWPORT
from ..guards.base import ABORT, REPLAN, Context, Guard
from ..models import prompts
from ..models.base import Request
from ..models.text_parsers import parse_rule, parse_subtask
from ..models.uitars import parse_action
from .trajectory import Trajectory


class Hierarchical:
    architecture = "hierarchical"

    def __init__(self, planner, executor, guard: Guard, max_steps: int = 12, max_replans: int = 6,
                 executor_coords: str = "abs", planner_tokens: int = 160, executor_tokens: int = 256):
        self.planner, self.executor, self.guard = planner, executor, guard
        self.max_steps, self.max_replans, self.coords = max_steps, max_replans, executor_coords
        self.planner_tokens, self.executor_tokens = planner_tokens, executor_tokens

    def _call(self, model, role: str, req: Request, step: int, traj: Trajectory) -> str:
        t0 = time.perf_counter()
        out = model.generate([req])[0]
        traj.model_call(step=step, role=role, model=model.name, output=out, seconds=time.perf_counter() - t0)
        return out

    def _plan(self, task: str, finished, png: bytes, step: int, traj: Trajectory) -> Optional[str]:
        history = "; ".join(finished) if finished else "none"
        if self.guard.planner_mode == "rule":
            out = self._call(self.planner, "planner", Request(prompts.RULE_PLANNER.format(task=task, history=history),
                                                              png, self.planner_tokens), step, traj)
            parsed = parse_rule(out)
            return None if parsed is None else parsed[0]
        out = self._call(self.planner, "planner", Request(prompts.PLANNER.format(task=task, history=history),
                                                          png, self.planner_tokens), step, traj)
        return parse_subtask(out)

    def run(self, env, scenario) -> Trajectory:
        traj = Trajectory(scenario.id, self.architecture, self.guard.name)
        obs = env.reset(scenario)
        finished, replans = [], 0

        def new_subtask(o) -> Optional[Context]:
            text = self._plan(scenario.task, finished, o.png, o.step, traj)
            if text is None:
                return None
            traj.subtask(step=o.step, text=text)
            c = Context(env=env, task=scenario.task, subtask=text, subtask_step=o.step, subtask_png=o.png,
                        step=o.step, png=o.png, trajectory=traj)
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
                replans += 1
                if replans > self.max_replans:
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
                replans += 1
                if replans > self.max_replans:
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
