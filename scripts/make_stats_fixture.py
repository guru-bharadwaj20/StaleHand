"""Write a synthetic two-arm result file and the Python statistics on it, so other implementations
(crates/stalestats) can check they agree. The rows are made up; they are not experiment results."""
import json
import random
from pathlib import Path

from stalehand.metrics import stats

OUT = Path(__file__).resolve().parents[1] / "schema" / "fixtures"


def main():
    rng = random.Random(7)
    rows = []
    for t in range(30):
        easy = rng.random() < 0.5  # templates differ in difficulty, so outcomes correlate within a template
        for v in ("L0", "L1", "L3"):
            sid = f"synthetic-relative-{t:03d}-{v}"
            for guard, p in (("rule_subtask", 0.9 if easy else 0.6), ("none", 0.6 if easy else 0.1)):
                rows.append({"scenario_id": sid, "guard": guard, "outcome": "success" if rng.random() < p else "stale"})
    with open(OUT / "results_pair.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    a = [r for r in rows if r["guard"] == "rule_subtask"]
    b = [r for r in rows if r["guard"] == "none"]
    expected = stats.compare(a, b, n_boot=10000, seed=0)
    (OUT / "results_pair.expected.json").write_text(json.dumps(expected, indent=1) + "\n")
    print(json.dumps(expected))


if __name__ == "__main__":
    main()
