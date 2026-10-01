"""The model interface every backend implements, plus a scripted model for tests."""
from dataclasses import dataclass
from typing import Callable, List, Optional, Protocol, Sequence, Tuple, Union


@dataclass(frozen=True)
class Request:
    prompt: str
    image_png: Optional[bytes] = None
    max_new_tokens: int = 256


class VLM(Protocol):
    name: str

    def generate(self, requests: Sequence[Request]) -> List[str]:
        """Greedy completions, one per request, in order."""


Rule = Tuple[Union[str, Callable[[Request], bool]], str]


class ScriptedVLM:
    """Answers with the reply of the first rule whose substring (or predicate) matches the prompt."""

    def __init__(self, rules: Sequence[Rule], name: str = "scripted"):
        self.rules, self.name, self.calls = list(rules), name, []

    def _reply(self, r: Request) -> str:
        for match, reply in self.rules:
            if (match(r) if callable(match) else match in r.prompt):
                return reply
        raise LookupError(f"no scripted reply for prompt: {r.prompt[:80]!r}")

    def generate(self, requests: Sequence[Request]) -> List[str]:
        self.calls.extend(requests)
        return [self._reply(r) for r in requests]
