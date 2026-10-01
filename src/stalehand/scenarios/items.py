"""An item is one selectable thing on screen: an email row, a product listing, a file."""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class Item:
    id: str
    attrs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "attrs", MappingProxyType(dict(self.attrs)))

    def get(self, name: str) -> Any:
        return self.attrs.get(name)
