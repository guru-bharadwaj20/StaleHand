"""Parsers for the free-text fields the planner and checker prompts ask for."""
import re
from typing import Optional, Tuple


def parse_subtask(text: str) -> Optional[str]:
    """The planner's next subtask, or None when it says the task is done."""
    m = re.search(r"Subtask:\s*(.+)", text)
    line = (m.group(1) if m else text).strip().splitlines()[0].strip()
    return None if line.upper().rstrip(".") == "DONE" else line


def parse_rule(text: str) -> Optional[Tuple[str, str]]:
    """(subtask for the executor, the bare rule) from a rule-subtask planner reply; None when done."""
    r = re.search(r"Target rule:\s*(.+)", text)
    a = re.search(r"Action:\s*(.+)", text)
    rule = r.group(1).strip() if r else text.strip().splitlines()[0]
    if rule.upper().rstrip(".") == "DONE":
        return None
    act = a.group(1).strip() if a else "click it"
    return f"{act} - the element that matches this rule: {rule}", rule


def parse_verdict(text: str) -> str:
    m = re.search(r"Verdict:\s*(VALID|STALE)", text, re.I)
    return m.group(1).upper() if m else "UNPARSED"


def parse_description(text: str) -> str:
    """The element description inside click("...") from a two-stage (describe, then ground) worker."""
    m = re.search(r'click\(\s*["\'](.+?)["\']\s*\)', text, re.S)
    return (m.group(1) if m else text.split("Action:")[-1]).strip()
