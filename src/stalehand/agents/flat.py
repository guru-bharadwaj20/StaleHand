"""One policy per step (Agent S3 style): the executor gets the whole task and its own action history on every step,
with no planner and so no subtask to go stale. It is the reference the planner-based architectures are compared to.

Guards still see each step; a re-plan has nothing to re-plan, so it means "take a fresh screenshot and decide again".
"""
import time

from ..env.actions import Done, Wait
from ..env.browser import VIEWPORT
from ..guards.base import ABORT, REPLAN, Context, Guard
from ..models import prompts
from ..models.base import Request
from ..models.uitars import parse_action
from .trajectory import Trajectory


class Flat:
    architecture = "flat"

    def __init__(self, planner, executor, guard: Guard, max_steps: int = 12, max_replans: int = 3,
                 executor_coords: str = "abs", executor_tokens: int = 256, **_):
        self.executor, self.guard = executor, guard
        self.max_steps, self.max_replans, self.coords = max_steps, max_replans, executor_coords
        self.executor_tokens = executor_tokens

    def run(self, env, scenario) -> Trajectory:
        traj = Trajectory(scenario.id, self.architecture, self.guard.name)
        obs = env.reset(scenario)
        ctx = Context(env=env, task=scenario.task, subtask=scenario.task, subtask_step=0, subtask_png=obs.png,
                      step=0, png=obs.png, trajectory=traj)
        self.guard.on_subtask(ctx)
        history, replans = [], {}
        while env.step < self.max_steps:
            ctx.step, ctx.png, ctx.action = obs.step, obs.png, None
            decision = self.guard.before_think(ctx)
            traj.decision(step=obs.step, guard=self.guard.name, decision=decision, moment="think")
            if decision == ABORT:
                return self._end(traj, env, "guard_abort")
            req = Request(prompts.EXECUTOR.format(instruction=scenario.task,
                                                  history="\n".join(history) if history else "none"),
                          obs.png, self.executor_tokens)
            t0 = time.perf_counter()
            raw = self.executor.generate([req])[0]
            traj.model_call(step=obs.step, role="executor", model=self.executor.name, output=raw,
                            seconds=time.perf_counter() - t0)
            action = parse_action(raw, VIEWPORT, self.coords)
            if isinstance(action, Done):
                traj.action(step=obs.step, action=action, raw=raw)
                return self._end(traj, env, "executor_done")
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
                continue
            traj.action(step=obs.step, action=action, raw=raw)
            obs = env.act(action if action is not None else Wait())
            history.append(f"{len(history) + 1}. {raw.strip().splitlines()[-1] if raw.strip() else 'none'}")
        return self._end(traj, env, "max_steps")

    @staticmethod
    def _end(traj: Trajectory, env, reason: str) -> Trajectory:
        traj.finish(reason=reason, app_events=env.events())
        return traj
