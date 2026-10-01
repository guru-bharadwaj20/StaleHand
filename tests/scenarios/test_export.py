import json

from stalehand.scenarios import registry
from stalehand.scenarios.export import read_jsonl, write_jsonl


def test_jsonl_roundtrip(tmp_path):
    scen = registry.generate("shop", seed=1, n=2)
    path = tmp_path / "s.jsonl"
    write_jsonl(scen, path)
    assert read_jsonl(path) == scen


def test_one_scenario_per_line_with_derived_fields(tmp_path):
    scen = registry.generate("inbox", seed=0, n=1, kinds=["relative"], variants=["L1"])
    path = tmp_path / "s.jsonl"
    write_jsonl(scen, path)
    rows = [json.loads(l) for l in path.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["derived"] == {"stale_target": scen[0].stale_target,
                                  "final_target": scen[0].target_at(scen[0].last_change_step),
                                  "change_kind": "relevant"}


def test_tampered_derived_target_is_rejected(tmp_path):
    import pytest
    scen = registry.generate("inbox", seed=0, n=1, kinds=["relative"], variants=["L1"])
    path = tmp_path / "s.jsonl"
    write_jsonl(scen, path)
    row = json.loads(path.read_text())
    row["derived"]["final_target"] = "m00"
    path.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError):
        read_jsonl(path)
