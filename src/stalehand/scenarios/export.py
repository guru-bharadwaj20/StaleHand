"""Write scenario sets to JSONL and read them back. Derived ground truth is stored too, for other languages."""
import json
from pathlib import Path
from typing import Iterable, List

from .scenario import Scenario
from .serialize import scenario_from_dict, scenario_to_dict


def derived(s: Scenario) -> dict:
    return {"stale_target": s.stale_target, "final_target": s.target_at(s.last_change_step),
            "change_kind": s.change_kind}


def write_jsonl(scenarios: Iterable[Scenario], path) -> int:
    n = 0
    with open(path, "w") as f:
        for s in scenarios:
            row = scenario_to_dict(s)
            row["derived"] = derived(s)
            f.write(json.dumps(row, sort_keys=True) + "\n")
            n += 1
    return n


def read_jsonl(path) -> List[Scenario]:
    """Read scenarios; if a row carries derived fields, they must match what the data gives."""
    out = []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        s = scenario_from_dict(row)
        if "derived" in row and row["derived"] != derived(s):
            raise ValueError(f"derived fields of {s.id} do not match its data")
        out.append(s)
    return out
