import json
from pathlib import Path

from jsonschema import Draft202012Validator

from stalehand.agents.trajectory import Trajectory
from stalehand.metrics.outcome import score
from stalehand.scenarios.domains import shop

SCHEMA = json.loads((Path(__file__).parents[2] / "schema" / "result.schema.json").read_text())


def test_scored_rows_match_result_schema():
    Draft202012Validator.check_schema(SCHEMA)
    s = shop.build(seed=0, kind="cheapest", index=0, variant="L1")
    for events, reason in (([], "guard_abort"), ([{"kind": "add_to_cart", "itemId": s.stale_target, "commit": True, "step": 3}], "planner_done")):
        t = Trajectory(s.id, "hierarchical", "none")
        t.finish(reason, events)
        row = json.loads(json.dumps(score(s, t)))
        errors = list(Draft202012Validator(SCHEMA).iter_errors(row))
        assert not errors, errors[0].message
