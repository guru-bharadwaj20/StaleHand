import json

import pytest

from stalehand.report.tables import load_rows, rates


def row(guard, outcome, change_kind="relevant", kind="relative", false_alarm=False, planner_calls=1, sid="s"):
    return {"scenario_id": sid, "guard": guard, "outcome": outcome, "change_kind": change_kind, "kind": kind,
            "false_alarm": false_alarm, "planner_calls": planner_calls, "architecture": "hierarchical"}


def test_rates_group_and_count_outcomes():
    rows = [row("none", "stale"), row("none", "success"), row("none", "stale", planner_calls=3),
            row("replan_every_step", "success", planner_calls=5)]
    out = rates(rows, by=("guard",))
    none = next(r for r in out if r["guard"] == "none")
    assert none["n"] == 3 and none["success"] == 1 and none["stale"] == 2
    assert none["success_rate"] == pytest.approx(1 / 3) and none["stale_rate"] == pytest.approx(2 / 3)
    assert none["planner_calls"] == pytest.approx(5 / 3)
    assert [r["guard"] for r in out] == ["none", "replan_every_step"]  # first-seen order


def test_false_alarm_rate_only_counts_harmless_changes():
    rows = [row("g", "success", change_kind="none", false_alarm=True),
            row("g", "success", change_kind="irrelevant", false_alarm=False),
            row("g", "stale", change_kind="relevant", false_alarm=False)]
    (r,) = rates(rows, by=("guard",))
    assert r["false_alarm_rate"] == pytest.approx(1 / 2)


def test_false_alarm_rate_is_none_without_harmless_changes():
    (r,) = rates([row("g", "stale")], by=("guard",))
    assert r["false_alarm_rate"] is None


def test_load_rows_reads_every_run_directory(tmp_path):
    for job, rs in {"a": [row("none", "stale")], "b": [row("x", "success"), row("x", "stale")]}.items():
        d = tmp_path / "pilot" / job
        d.mkdir(parents=True)
        (d / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs))
    assert len(load_rows(tmp_path)) == 3


def test_guard_summary_splits_relevant_and_harmless():
    from stalehand.report.tables import guard_summary
    rows = [row("g", "success", change_kind="relevant", planner_calls=2),
            row("g", "stale", change_kind="relevant", planner_calls=2),
            row("g", "success", change_kind="none", false_alarm=True, planner_calls=4),
            row("g", "no_commit", change_kind="irrelevant", planner_calls=4)]
    for r in rows:
        r["checker_calls"] = 1
    (s,) = guard_summary(rows)
    assert s["guard"] == "g" and s["relevant_n"] == 2 and s["harmless_n"] == 2
    assert s["relevant_success"] == pytest.approx(0.5) and s["relevant_stale"] == pytest.approx(0.5)
    assert s["harmless_success"] == pytest.approx(0.5) and s["false_alarm"] == pytest.approx(0.5)
    assert s["calls"] == pytest.approx(4.0)  # planner + checker calls per episode: (3 + 3 + 5 + 5) / 4
