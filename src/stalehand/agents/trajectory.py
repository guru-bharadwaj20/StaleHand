"""Everything that happened in one episode, in order, as JSON-ready entries."""
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..env.actions import action_to_dict


@dataclass
class Trajectory:
    scenario_id: str
    architecture: str
    guard: str
    entries: List[Dict[str, Any]] = field(default_factory=list)
    end_reason: Optional[str] = None
    app_events: List[Dict[str, Any]] = field(default_factory=list)

    def model_call(self, step: int, role: str, model: str, output: str, seconds: float, **extra) -> None:
        self.entries.append({"kind": "model_call", "step": step, "role": role, "model": model, "output": output,
                             "seconds": round(seconds, 4), **extra})

    def decision(self, step: int, guard: str, decision: str, **extra) -> None:
        self.entries.append({"kind": "decision", "step": step, "guard": guard, "decision": decision, **extra})

    def action(self, step: int, action, raw: str) -> None:
        self.entries.append({"kind": "action", "step": step, "raw": raw,
                             "action": None if action is None else action_to_dict(action)})

    def subtask(self, step: int, text: str, **extra) -> None:
        self.entries.append({"kind": "subtask", "step": step, "text": text, **extra})

    def stall(self, step: int, actions: int) -> None:
        self.entries.append({"kind": "stall", "step": step, "actions": actions})

    def finish(self, reason: str, app_events: List[Dict[str, Any]]) -> None:
        self.end_reason, self.app_events = reason, list(app_events)

    def calls_by_role(self) -> Dict[str, int]:
        return dict(Counter(e["role"] for e in self.entries if e["kind"] == "model_call"))

    def parse_failures(self) -> int:
        return sum(1 for e in self.entries if e["kind"] == "action" and e["action"] is None)

    def to_dict(self) -> Dict[str, Any]:
        return {"scenario_id": self.scenario_id, "architecture": self.architecture, "guard": self.guard,
                "end_reason": self.end_reason, "entries": self.entries, "app_events": self.app_events}
