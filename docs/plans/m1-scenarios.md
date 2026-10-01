# M1 plan: scenario core

**Goal:** deterministic scenario data with computed ground truth, for the inbox and shop domains, exportable to
JSONL from the command line. No browser and no models in this milestone.

**Architecture:** pure Python under `src/stalehand/scenarios/`. Items are immutable records; a criterion selects
the target; change events are pure functions from item lists to item lists; relevance is computed by resolving
before and after a change.

## Files

| File | Responsibility |
|---|---|
| `scenarios/items.py` | `Item(id: str, attrs: Mapping[str, Any])`, frozen; `Item.get(name)` |
| `scenarios/criteria.py` | `Order(field: str, descending: bool)`, `Criterion(filters: tuple[tuple[str, Any], ...], order: Order or None)`, `is_relative` |
| `scenarios/resolve.py` | `Resolution(target: str or None, status: "unique" / "none" / "ambiguous")`, `resolve(items, criterion)` |
| `scenarios/changes.py` | `Insert`, `Remove`, `Update`, `Sort`, `Cosmetic`; `apply(items, change) -> list[Item]` |
| `scenarios/relevance.py` | `classify(before, after, criterion) -> "relevant" / "irrelevant" / "none" / "target_removed"` |
| `scenarios/scenario.py` | `ScheduledChange(step, change)`, `Scenario`, `items_after(step)`, `stale_target`, `target_at(step)`, `to_dict` / `from_dict` |
| `scenarios/serialize.py` | change and criterion (de)serialisation |
| `scenarios/domains/inbox.py` | inbox generator: fixed and relative tasks, 0/1/3 new emails from the sender, irrelevant arrivals |
| `scenarios/domains/shop.py` | shop generator: cheapest and highest-rated tasks, new listings, price updates |
| `scenarios/registry.py` | domain lookup by name |
| `scenarios/export.py` | `write_jsonl(scenarios, path)`, `read_jsonl(path)` |
| `cli.py` | `stalehand scenarios --domain inbox --n 40 --seed 0 --out path.jsonl` |

## Tests (written first)

Resolver:
- equality filters select the only matching item; no match gives `none`; two matches without an order give
  `ambiguous`.
- newest-first ordering picks the maximum; ascending picks the minimum; a tie at the top gives `ambiguous`.
- filters and ordering combine (newest email from one sender among many senders).
- a missing attribute never matches a filter and never wins an ordering.

Changes:
- insert at the top and at a position; insert of a duplicate id is rejected.
- remove an id; removing a missing id is rejected.
- update merges attributes without touching other items; input lists are never mutated.
- sort orders by a field; cosmetic returns an equal list.

Relevance:
- a newer email from the sender is `relevant`; an email from another sender is `irrelevant`; cosmetic is `none`;
  removing the target is `target_removed`; a price drop below the cheapest item is `relevant`.

Scenario:
- `target_at(step)` applies only changes scheduled at or before that step.
- JSON round trip gives an equal scenario.
- generators are deterministic for a seed and differ across seeds.
- every generated scenario's stated relevance matches `classify`, and its stale and final targets resolve
  uniquely.

## Order of work

1. Items and criteria. 2. Resolver, one behaviour per test. 3. Changes. 4. Relevance. 5. Scenario and round trip.
6. Inbox generator. 7. Shop generator. 8. Registry, export and CLI. 9. Progress note.
