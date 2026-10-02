"""Parse UI-TARS style action strings into environment actions.

Coordinates come either in screen pixels ("abs", what UI-TARS-1.5 emits when the screenshot is not resized) or
on a 0-1000 grid ("rel1000", what some other grounders emit). The caller picks the mode per model.
"""
import re
from typing import Optional, Tuple

from ..env.actions import Click, Done, Key, Scroll, Type, Wait

_ACTION = re.compile(r"Action:\s*([a-z_]+)\((.*)\)\s*$", re.S)
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_GROUP = re.compile(r"\[\[[^\]]*\]\]|\([^()]*\)")
_KEYS = {"enter": "Enter", "return": "Enter", "tab": "Tab", "esc": "Escape", "escape": "Escape", "space": " ",
         "backspace": "Backspace", "delete": "Delete", "ctrl": "Control", "control": "Control", "alt": "Alt",
         "shift": "Shift", "cmd": "Meta", "meta": "Meta", "up": "ArrowUp", "down": "ArrowDown",
         "left": "ArrowLeft", "right": "ArrowRight", "pagedown": "PageDown", "pageup": "PageUp"}
SCROLL_PX = 300


def _arg(args: str, name: str) -> Optional[str]:
    m = re.search(rf"{name}\s*=\s*'((?:[^'\\]|\\.)*)'", args)
    return None if m is None else m.group(1)


def _unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")


def _point(args: str, screen: Tuple[int, int], mode: str) -> Optional[Tuple[int, int]]:
    raw = _arg(args, "start_box") or _arg(args, "point")
    if raw is None:  # some models drop the closing quote: take the rest of the arguments
        m = re.search(r"(?:start_box|point)\s*=\s*'(.*)", args, re.S)
        raw = m.group(1) if m else ""
    groups = _GROUP.findall(raw)  # a label may precede the box ("8:37 AM[[944, 797, 980, 815]]"): use the box
    nums = [float(n) for n in _NUM.findall(groups[-1] if groups else raw)]
    if len(nums) == 4:
        nums = [(nums[0] + nums[2]) / 2, (nums[1] + nums[3]) / 2]
    if len(nums) != 2:
        return None
    x, y = nums
    if mode == "rel1000":
        x, y = x * screen[0] / 1000, y * screen[1] / 1000
    elif mode != "abs":
        raise ValueError(f"unknown coordinate mode {mode!r}")
    return min(max(int(round(x)), 0), screen[0] - 1), min(max(int(round(y)), 0), screen[1] - 1)


def _key(spec: str) -> str:
    return "+".join(_KEYS.get(k.lower(), k) for k in spec.split())


def parse_action(text: str, screen: Tuple[int, int], mode: str = "abs"):
    """Return an env action, or None when the output holds no usable action."""
    if mode not in ("abs", "rel1000"):
        raise ValueError(f"unknown coordinate mode {mode!r}")
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("Action:")]
    m = _ACTION.search(lines[-1].strip()) if lines else None
    if m is None:
        return None
    kind, args = m.group(1), m.group(2)
    if kind in ("click", "left_single", "left_double", "right_single"):
        pt = _point(args, screen, mode)
        return None if pt is None else Click(*pt)
    if kind == "type":
        content = _arg(args, "content")
        return None if content is None else Type(_unescape(content))
    if kind == "hotkey":
        key = _arg(args, "key")
        return None if not key else Key(_key(key))
    if kind == "scroll":
        direction = (_arg(args, "direction") or "down").lower()
        dx, dy = {"down": (0, SCROLL_PX), "up": (0, -SCROLL_PX), "right": (SCROLL_PX, 0), "left": (-SCROLL_PX, 0)}.get(direction, (0, 0))
        return Scroll(dx, dy)
    if kind == "wait":
        return Wait()
    if kind == "finished":
        return Done(_unescape(_arg(args, "content") or ""))
    return None
