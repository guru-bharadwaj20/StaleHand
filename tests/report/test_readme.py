import json

import pytest

from stalehand.report.readme import END, START, section, splice


def row(guard, outcome, change_kind="relevant", false_alarm=False, planner_calls=1, seconds=2.0):
    return {"scenario_id": "inbox-relative-000-L1", "guard": guard, "outcome": outcome, "change_kind": change_kind,
            "kind": "relative", "false_alarm": false_alarm, "planner_calls": planner_calls,
            "model_seconds": seconds, "architecture": "hierarchical", "run": {"executor": "ui-tars-1.5-7b"}}


def write(path, rows):
    path.mkdir(parents=True)
    (path / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_section_has_one_table_per_run_set(tmp_path):
    write(tmp_path / "vivian-4090" / "pilot" / "a", [row("none", "stale"), row("none", "success")])
    write(tmp_path / "guru-4500" / "domains" / "b", [row("rebind_step", "success", planner_calls=3)])
    text = section(tmp_path)
    assert text.index("### `guru-4500/domains`") < text.index("### `vivian-4090/pilot`")
    assert "| none | 2 | 1 | 50% | 50% | n/a | 1.0 | 2.0 |" in text
    assert "| rebind_step | 1 | 1 | 100% | 0% | n/a | 3.0 | 2.0 |" in text


def test_stale_rate_is_over_relevant_changes_and_false_alarms_over_harmless(tmp_path):
    write(tmp_path / "m" / "x" / "j", [row("g", "stale"), row("g", "success", change_kind="none", false_alarm=True),
                                       row("g", "success", change_kind="irrelevant")])
    assert "| g | 3 | 2 | 67% | 100% | 50% |" in section(tmp_path)


def test_splice_replaces_only_between_markers():
    doc = f"# T\n\n{START}\nold\n{END}\n\nrest\n"
    assert splice(doc, "new\n") == f"# T\n\n{START}\nnew\n{END}\n\nrest\n"


def test_splice_needs_markers():
    with pytest.raises(ValueError):
        splice("# no markers\n", "x")
