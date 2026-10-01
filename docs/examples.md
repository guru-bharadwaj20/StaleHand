# Worked examples

Two examples. The first runs one scenario from generation to a scored row. The second adds a new domain.
Commands run from the repository root.

## One scenario end to end

[`examples/one_scenario.py`](../examples/one_scenario.py) needs no GPU. It needs Chrome and a built
`apps/dist` (`cd apps && npm run build`).

```bash
.venv/bin/python examples/one_scenario.py      # Windows: .venv\Scripts\python
```

The planner and executor in it are scripted stand-ins for the vision models. The planner names the product it
sees on screen. The executor clicks the product the subtask names, then Add to cart. That is the behaviour that
goes stale.

### 1. Generate

```python
s = shop.build(seed=0, kind="cheapest", index=0, variant="L1", change_step=0)
```

Every domain module has the same `build(seed, kind, index, variant, change_step)`. This one is a "cheapest"
shop task. The `L1` variant slips one cheaper product in above the old cheapest. The script prints:

```text
task:           Add the cheapest USB-C cable on this page to the cart.
change kind:    relevant
planner sees:   p06 Nylon Braid
correct after:  q0 Basics Cable
scenario JSON:  1998 bytes, as `stalehand scenarios` writes it
```

`s.stale_target` is the answer on the first screen. `s.target_at(s.last_change_step)` is the answer after the
change. `scenario_to_dict(s)` is the same JSON line that `stalehand scenarios` writes.

### 2. Run it in the live shop

```python
env = SeeingEnv(change_timing="after_handoff")
agent = Hierarchical(Planner(env, s), Executor(env, s), guards.make(guard), max_steps=6)
traj = agent.run(env, s)
```

`SeeingEnv` is a `BrowserEnv` that remembers when a change reached the page, so the scripted planner can
"see" it. With `change_timing="after_handoff"` and `change_step=0`, the cheaper product arrives after the
planner writes its first subtask and before the executor looks.

The script runs the same scenario under two guards:

```text
[none]
  subtasks:       ['Add the Nylon Braid to the cart.']
  added to cart:  p06 Nylon Braid
  outcome:        stale (planner calls 2)

[replan_every_step]
  subtasks:       ['Add the Nylon Braid to the cart.', 'Add the Basics Cable to the cart.', 'Add the Basics Cable to the cart.', 'Add the Basics Cable to the cart.']
  added to cart:  q0 Basics Cable
  outcome:        success (planner calls 5)
```

With no guard, the executor follows the old subtask and buys the old cheapest. That is `stale`. With
`replan_every_step`, the planner looks again before each step, sees the new product and rewrites the subtask.
That is `success`, at the cost of more planner calls.

### 3. Score

```python
row = score(s, traj)
```

`score` (in `stalehand.metrics.outcome`) returns one dict per episode. It is the same row a job writes to
`results.jsonl`. The fields:

| Field | Meaning |
|---|---|
| `scenario_id`, `guard`, `architecture`, `kind`, `variant`, `change_kind` | what was run |
| `outcome` | `success`, `stale`, `wrong_item`, `wrong_detail`, `aborted` or `no_commit` |
| `target`, `correct_target`, `stale_target` | item committed to, the right one, the one the planner first saw |
| `end_reason` | why the episode stopped |
| `fired`, `false_alarm` | how often the guard fired, and whether it fired with nothing to catch |
| `planner_calls`, `executor_calls`, `checker_calls`, `model_seconds` | cost |
| `env_steps`, `parse_failures` | actions taken, model replies that did not parse |
| `commit_step`, `commit_before_change` | when the commit happened, and whether it beat the change |

### 4. The same scenario as a matrix job

In a real run the models replace the scripted stand-ins, and the runner does the loop above. The scenario comes
from a JSONL file instead of `shop.build`:

```bash
python -m stalehand scenarios --domain shop --n 5 --seed 0 --change-step 0 --out shop.jsonl
```

This writes the scenario above (`shop-cheapest-000-L1`) along with every other kind, index and variant.
`experiments/main/make_scenarios.sh` does this and splits the file into shards of 10. The matrix then lists
the shards and the other axes:

```json
{
  "name": "main",
  "scenarios": ["experiments/main/shards/shop-00.jsonl", "..."],
  "architectures": ["hierarchical"],
  "guards": ["none", "replan_every_step", "..."],
  "planners": ["qwen3-vl-8b"],
  "executors": ["ui-tars-1.5-7b"],
  "seeds": [0],
  "max_steps": 12,
  "timings": ["after_handoff"]
}
```

Each combination of shard, guard, model pair, seed and timing becomes one job. Plan and run it as in
[usage.md](usage.md#3-run-a-matrix):

```bash
runner/stalerun plan -db runs/main.db -matrix experiments/main/matrix.json
runner/stalerun run  -db runs/main.db -hosts runner/hosts.json -logs runs/logs
```

Each scored row lands in `runs/main/<job id>/results.jsonl`, and `stalehand report` compares guards from there.

## Adding a new domain

A domain is a scenario generator in Python and an app in TypeScript. Both are found by name, so you only add
files. Nothing shared needs editing:

- `stalehand.scenarios.registry` imports every module in `src/stalehand/scenarios/domains/` that defines
  `build`, `KINDS` and `VARIANTS`. The module name is the domain name.
- `apps/build.mjs` builds every `apps/src/<name>/main.ts` into `apps/dist/<name>.html`.
- `BrowserEnv` opens `apps/dist/<scenario.domain>.html`.

So the Python module name, the app directory and `Scenario.domain` must all be the same word. The `files`
domain is a good model to copy. Below, the new domain is called `notes`.

### Files to add

| File | What it holds |
|---|---|
| `src/stalehand/scenarios/domains/notes.py` | `KINDS`, `VARIANTS`, `build` |
| `src/stalehand/scenarios/domains/notes_data.py` | name pools (no `build`, so it is not a domain) |
| `apps/src/notes/main.ts` | entry point |
| `apps/src/notes/state.ts` | `initial`, `reduce`, `withChange` |
| `apps/src/notes/render.ts` | `mount` |
| `apps/src/notes/style.css` | styles |
| `tests/scenarios/domains/test_notes.py` | generator tests |
| `tests/scenarios/domains/test_notes_data.py` | data pool tests |
| `apps/test/notes-state.test.ts` | state machine tests |
| `tests/env/test_notes_browser.py` | browser tests (marked `browser`) |

### 1. The generator

`build` must be deterministic in its arguments. All variants of one `(seed, kind, index)` share the same first
screen, so seed the first-screen RNG without the variant, as `files.py` does:

```python
"""Notes scenarios: ..."""
import random

from ..changes import Cosmetic, Insert, Update
from ..criteria import Criterion, Order
from ..items import Item
from ..scenario import Scenario, ScheduledChange
from .notes_data import TITLES

KINDS = ("fixed", "relative")
VARIANTS = ("none", "cosmetic", "L0", "L1", "rename")


def build(seed: int, kind: str, index: int, variant: str, change_step: int = 1) -> Scenario:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    rng = random.Random(f"notes:{seed}:{kind}:{index}")   # no variant here
    items = [Item(f"n{i:02d}", {"title": ..., "modified": ...}) for i in range(10)]
    target = items[...]
    criterion = Criterion({"title": target.get("title")})  # or Criterion({...}, Order("modified", descending=True))
    task = f"Share {target.get('title')} with {recipient}."
    change = ...   # None, Cosmetic("label"), Insert((Item(...), ...)), Update(target.id, {...})
    changes = () if change is None else (ScheduledChange(change_step, change),)
    return Scenario(id=f"notes-{kind}-{index:03d}-{variant}", domain="notes", seed=seed, task=task,
                    criterion=criterion, items=tuple(items), changes=changes,
                    meta={"kind": kind, "variant": variant, "index": index, "action": "share",
                          "recipient": recipient, "change_step": change_step})
```

`meta["kind"]` and `meta["variant"]` go into the score row. `meta["action"]` tells `score` how to find the
commit: `"open"` means the last open event; anything else means the first event with `commit: true`. For
`share`, `assign` and `forward`, `score` also checks the event's `detail.to` against `meta["recipient"]`.

Once the module exists, `python -m stalehand scenarios --domain notes ...` works.

### 2. The app

`main.ts` is the same four lines in every app:

```ts
import { install } from "../core/harness.js";
import { Store } from "../core/store.js";
import { initial, reduce, withChange } from "./state.js";
import { mount } from "./render.js";

install((items) => new Store(initial(items), reduce, withChange), mount);
```

`state.ts` is a pure state machine. `reduce` returns the new state and the events it logs. The committing
action logs `commit: true` and the item id:

```ts
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export interface NotesState { items: Item[]; view: View; banner: string | null; }
export const initial = (items: Item[]): NotesState => ({ items, view: { name: "list" }, banner: null });

export function reduce(state: NotesState, action: NotesAction): { state: NotesState; events: ActionEvent[] } {
  // ... e.g. on send:
  // return { state: ..., events: [{ kind: "share", itemId: v.id, commit: true, detail: { to: v.to } }] };
}

export function withChange(state: NotesState, change: Change): NotesState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
```

`render.ts` exports `mount(root, store)`. It redraws on each store update. Rows carry both `data-item-id` and
`data-role`, and buttons and inputs carry `data-role`. `BrowserEnv.item_boxes()` and `BrowserEnv.role_box(role)` find them by
these attributes. See `apps/src/files/render.ts`.

Then rebuild: `cd apps && npm run build`. You get `apps/dist/notes.html`.

### 3. Tests

Copy the `files` tests and adapt them:

- `tests/scenarios/domains/test_files.py`: same arguments give the same scenario, variants share the first
  screen, each variant changes what it says it does.
- `apps/test/files-state.test.ts`: `reduce` and `withChange` on a small item list (`cd apps && npm test`).
- `tests/env/test_files_browser.py`: every row has a box, and the commit logs the right item and recipient.

Run `.venv/bin/pytest -m "not browser"`, then `.venv/bin/pytest -m browser`. Also add the new name to
`--domain` in [usage.md](usage.md) so people know it exists.
