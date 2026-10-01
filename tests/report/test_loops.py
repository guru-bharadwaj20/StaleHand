import json

from stalehand.report.loops import click_loop, loop_rows, markdown


def traj(end, clicks, extra=()):
    acts = [{"kind": "action", "step": i, "action": {"type": "click", "x": x, "y": y}} for i, (x, y) in enumerate(clicks)]
    acts += [{"kind": "action", "step": 99, "action": a} for a in extra]
    return {"scenario_id": "inbox-fixed-000-none", "end_reason": end, "entries": acts}


def test_four_clicks_on_one_spot_at_the_step_limit_is_a_loop():
    assert click_loop(traj("max_steps", [(10, 10), (280, 245), (280, 245), (287, 245), (280, 250)]))


def test_spread_clicks_or_an_early_end_are_not_loops():
    assert not click_loop(traj("max_steps", [(280, 245), (280, 245), (280, 245), (400, 245)]))
    assert not click_loop(traj("planner_done", [(280, 245)] * 6))
    assert not click_loop(traj("max_steps", [(280, 245)] * 3))
    assert not click_loop(traj("max_steps", [(280, 245)] * 4, extra=[{"type": "type", "text": "x"}]))


def test_loop_rows_join_trajectories_to_results(tmp_path):
    run = tmp_path / "main" / "job1"
    (run / "trajectories").mkdir(parents=True)
    (run / "results.jsonl").write_text(json.dumps({"scenario_id": "inbox-fixed-000-none", "architecture": "h",
                                                   "guard": "none", "outcome": "no_commit"}) + "\n")
    (run / "trajectories" / "inbox-fixed-000-none.json").write_text(json.dumps(traj("max_steps", [(5, 5)] * 4)))
    rows = loop_rows(tmp_path / "main")
    assert rows == [{"run_set": "main", "architecture": "h", "guard": "none", "outcome": "no_commit",
                     "end_reason": "max_steps", "loop": True}]
    md = markdown(rows)
    assert "| main | h | none | 1 | 100% | 100% | 100% | 100% |" in md
