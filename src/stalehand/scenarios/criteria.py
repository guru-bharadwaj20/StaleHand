"""What the task asks for: equality filters, plus an ordering for relative tasks ("latest", "cheapest")."""
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple, Union


@dataclass(frozen=True)
class Order:
    field: str
    descending: bool = True


Filters = Tuple[Tuple[str, Any], ...]


@dataclass(frozen=True)
class Criterion:
    filters: Union[Filters, Mapping[str, Any]] = ()
    order: Optional[Order] = None

    def __post_init__(self):
        pairs = self.filters.items() if isinstance(self.filters, Mapping) else self.filters
        object.__setattr__(self, "filters", tuple(sorted((str(k), v) for k, v in pairs)))
        if not self.filters and self.order is None:
            raise ValueError("a criterion needs at least one filter or an order")

    @property
    def is_relative(self) -> bool:
        return self.order is not None
