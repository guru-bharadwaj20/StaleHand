"""Orchestrator and GUI operator (CoAct-1 style): the orchestrator hands over a whole goal; the operator works on it
alone for up to a fixed number of actions and reports back in one line. The orchestrator never sees the screens in
between, so a goal written before a change can stay in force for many steps.
"""
from typing import Optional

from ..models import prompts
from .hierarchical import Hierarchical


class Delegated(Hierarchical):
    architecture = "delegated"
    plain_prompt = prompts.ORCHESTRATOR

    def __init__(self, planner, executor, guard, operator_budget: int = 8, **kwargs):
        super().__init__(planner, executor, guard, **kwargs)
        self.subtask_budget = operator_budget

    def _report(self, subtask: str, message: Optional[str]) -> str:
        if message is None:
            return f"{subtask} (operator stopped: step budget of {self.subtask_budget} used up)"
        return f"{subtask} (operator report: {message or 'done'})"
