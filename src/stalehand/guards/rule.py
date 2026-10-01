"""Rule subtask: the planner writes the target as a rule in the task's own words ("the most recent email from
Samuel Lee") instead of naming a subject line, and the executor resolves it on the live screen."""
from .base import Guard


class RuleSubtask(Guard):
    name = "rule_subtask"
    planner_mode = "rule"
