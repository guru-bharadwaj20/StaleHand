import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from stalehand.scenarios import registry
from stalehand.scenarios.export import derived
from stalehand.scenarios.serialize import scenario_to_dict

SCHEMA = json.loads((Path(__file__).parents[2] / "schema" / "scenario.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def test_schema_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("domain", sorted(registry.DOMAINS))
def test_generated_scenarios_match_schema(domain):
    for s in registry.generate(domain, seed=0, n=3):
        row = scenario_to_dict(s) | {"derived": derived(s)}
        errors = list(VALIDATOR.iter_errors(row))
        assert not errors, f"{s.id}: {errors[0].message}"


def test_schema_rejects_unknown_change_type():
    row = scenario_to_dict(registry.generate("inbox", seed=0, n=1, variants=["L1"])[0])
    row["changes"][0]["change"] = {"type": "explode"}
    assert not VALIDATOR.is_valid(row)
