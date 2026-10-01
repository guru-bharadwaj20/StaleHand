"""The shared fixtures must match what the generators produce now; rerun scripts/make_fixtures.sh if not."""
from pathlib import Path

import pytest

from stalehand.scenarios import registry
from stalehand.scenarios.export import write_jsonl

FIXTURES = Path(__file__).parents[2] / "schema" / "fixtures"


@pytest.mark.parametrize("domain", ["inbox", "shop", "files", "tickets"])
def test_fixture_is_current(domain, tmp_path):
    fresh = tmp_path / f"{domain}.jsonl"
    write_jsonl(registry.generate(domain, seed=0, n=2), fresh)
    assert fresh.read_text() == (FIXTURES / f"{domain}.jsonl").read_text()
