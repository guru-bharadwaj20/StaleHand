"""The guard interface and the context the agent loop hands to it.

A guard sees two moments per executor step:
  before_think  the executor has a fresh screenshot but has not been called yet (cheap place to re-plan)
  before_act    the executor chose an action; the page may have changed since its screenshot (mid_step timing)
Each returns "proceed", "replan" or "abort".
"""
from dataclasses import dataclass, field
from typing import Any, Optional

PROCEED, REPLAN, ABORT = "proceed", "replan", "abort"


@dataclass
class Context:
    env: Any
    task: str
    subtask: str
    subtask_step: int          # env step at which the current subtask was written
    subtask_png: bytes         # screenshot the planner saw when writing it
    step: int                  # current env step
    png: bytes                 # current screenshot
    action: Optional[Any] = None   # set at before_act
    trajectory: Optional[Any] = None  # guards that call models record those calls here
    extra: dict = field(default_factory=dict)


class Guard:
    name = "none"
    planner_mode = "plain"     # "plain" subtasks, or "rule" subtasks written in the task's own words

    def on_subtask(self, ctx: Context) -> None:
        """Called whenever a new subtask is written."""

    def before_think(self, ctx: Context) -> str:
        return PROCEED

    def before_act(self, ctx: Context) -> str:
        return PROCEED
