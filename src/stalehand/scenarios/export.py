"""Write scenario sets to JSONL and read them back. Derived ground truth is stored too, for other languages."""
import json
from pathlib import Path
from typing import Iterable, List

from .scenario import Scenario
from .serialize import scenario_from_dict, scenario_to_dict


def write_jsonl(scenarios: Iterable[Scenario], path) -> int:
    n = 0
    with open(path, "w") as f:
        for s in scenarios:
            row = scenario_to_dict(s)
            row["derived"] = {"stale_target": s.stale_target, "final_target": s.target_at(s.last_change_step),
                              "change_kind": s.change_kind}
            f.write(json.dumps(row, sort_keys=True) + "\n")
            n += 1
    return n


def read_jsonl(path) -> List[Scenario]:
    return [scenario_from_dict(json.loads(line)) for line in Path(path).read_text().splitlines() if line.strip()]
