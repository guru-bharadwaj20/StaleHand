"""The shared statistics fixture must still match what this implementation computes."""
import json
from pathlib import Path

import pytest

from stalehand.metrics import stats

FIX = Path(__file__).parents[2] / "schema" / "fixtures"


def test_python_stats_match_shared_expected_values():
    rows = [json.loads(l) for l in (FIX / "results_pair.jsonl").read_text().splitlines()]
    expected = json.loads((FIX / "results_pair.expected.json").read_text())
    got = stats.compare([r for r in rows if r["guard"] == "rule_subtask"], [r for r in rows if r["guard"] == "none"],
                        n_boot=expected["n_boot"], seed=expected["seed"])
    assert got == pytest.approx(expected)
