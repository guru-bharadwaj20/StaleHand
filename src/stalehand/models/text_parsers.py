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


def parse_bound(text: str) -> Optional[Tuple[str, str, str, str]]:
    """(subtask, rule, target, action) from a bound-subtask planner reply; None when done or the target is missing.
    The executor gets the concrete target, as with a plain subtask; the rebind guard keeps the rule."""
    r = re.search(r"Target rule:\s*(.+)", text)
    t = re.search(r"^\s*Target:\s*(.+)", text, re.M)
    a = re.search(r"Action:\s*(.+)", text)
    if r is None or r.group(1).strip().upper().rstrip(".") == "DONE" or t is None:
        return None
    rule, target = r.group(1).strip(), t.group(1).strip()
    action = a.group(1).strip() if a else "click it"
    return f"{action} - {target}", rule, target, action


def parse_target(text: str) -> Optional[str]:
    """The element a resolve reply names, or None for NONE or an unparsed reply."""
    m = re.search(r"Target:\s*(.+)", text)
    if m is None:
        return None
    target = m.group(1).strip().strip("\"'")
    return None if target.upper().rstrip(".") == "NONE" else target


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", text.casefold()).split())


def same_target(a: str, b: str) -> bool:
    return _norm(a) == _norm(b)


def parse_verdict(text: str) -> str:
    m = re.search(r"Verdict:\s*(VALID|STALE)", text, re.I)
    return m.group(1).upper() if m else "UNPARSED"


def parse_description(text: str) -> str:
    """The element description inside click("...") from a two-stage (describe, then ground) worker."""
    m = re.search(r'click\(\s*["\'](.+?)["\']\s*\)', text, re.S)
    return (m.group(1) if m else text.split("Action:")[-1]).strip()
