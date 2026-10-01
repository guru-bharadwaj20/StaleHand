import json

from stalehand.report.recovery import first_open_missed, markdown, recovery_rows


def traj(*opens):
    return {"app_events": [{"kind": "page_change"}] + [{"kind": "open", "itemId": i} for i in opens]}


def test_first_open_missed_compares_the_first_opened_item_with_the_correct_one():
    assert first_open_missed(traj("m2", "m1"), "m1") is True
    assert first_open_missed(traj("m1", "m2"), "m1") is False
    assert first_open_missed(traj(), "m1") is None  # nothing opened


def test_recovery_table_splits_outcomes_after_a_missed_first_open(tmp_path):
    run = tmp_path / "timing" / "job1"
    (run / "trajectories").mkdir(parents=True)
    rows = [{"scenario_id": f"inbox-a-00{i}-L1", "architecture": "h", "guard": "none", "change_kind": "irrelevant",
             "outcome": o, "correct_target": "m1"} for i, o in enumerate(("success", "wrong_item", "success"))]
    (run / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    for r, opens in zip(rows, (("m2", "m1"), ("m2",), ("m1",))):
        (run / "trajectories" / f"{r['scenario_id']}.json").write_text(json.dumps(traj(*opens)))
    out = recovery_rows(tmp_path / "timing")
    assert [r["missed"] for r in out] == [True, True, False]
    assert "| timing | h | none | 3 | 67% | 50% | 50% |" in markdown(out)
