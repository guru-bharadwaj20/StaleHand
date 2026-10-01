"""Executor actions in screen pixels. Models' raw outputs are parsed into these elsewhere."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Click:
    x: int
    y: int

    def __post_init__(self):
        if self.x < 0 or self.y < 0:
            raise ValueError(f"click outside the screen: ({self.x}, {self.y})")


@dataclass(frozen=True)
class Type:
    text: str


@dataclass(frozen=True)
class Key:
    key: str


@dataclass(frozen=True)
class Scroll:
    dx: int
    dy: int


@dataclass(frozen=True)
class Done:
    message: str = ""


_KINDS = {"click": Click, "type": Type, "key": Key, "scroll": Scroll, "done": Done}
_NAMES = {v: k for k, v in _KINDS.items()}


def action_to_dict(action) -> dict:
    return {"type": _NAMES[type(action)], **asdict(action)}


def action_from_dict(d: dict):
    d = dict(d)
    kind = _KINDS.get(d.pop("type", None))
    if kind is None:
        raise ValueError(f"unknown action {d}")
    return kind(**d)
