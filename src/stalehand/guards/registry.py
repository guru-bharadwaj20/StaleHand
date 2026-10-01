"""Build guards from the names used in experiment matrices."""
import re

from .base import Guard
from .dom import DomChange
from .pixel import PixelChange
from .replan import ReplanEveryStep
from .rule import RuleSubtask
from .self_check import SelfCheck


def make(name: str, checker=None) -> Guard:
    if name == "none":
        return Guard()
    if name == "replan_every_step":
        return ReplanEveryStep()
    if name == "rule_subtask":
        return RuleSubtask()
    if name == "self_check":
        if checker is None:
            raise ValueError("self_check needs a checker model")
        return SelfCheck(checker)
    m = re.fullmatch(r"dom_(step|subtask)_(abort|replan)", name)
    if m:
        return DomChange(scope=m.group(1), on_change=m.group(2))
    m = re.fullmatch(r"pixel_([0-9.]+)_(abort|replan)", name)
    if m:
        return PixelChange(threshold=float(m.group(1)), on_change=m.group(2))
    raise KeyError(f"unknown guard {name!r}")
