import json

from stalehand.env.actions import Click
from stalehand.agents.trajectory import Trajectory


def test_records_calls_actions_and_decisions_in_order():
    t = Trajectory(scenario_id="s1", architecture="hierarchical", guard="none")
    t.model_call(step=0, role="planner", model="p", output="Subtask: open it", seconds=0.5)
    t.decision(step=1, guard="none", decision="proceed")
    t.action(step=1, action=Click(3, 4), raw="Action: click(start_box='(3,4)')")
    kinds = [e["kind"] for e in t.entries]
    assert kinds == ["model_call", "decision", "action"]
    assert t.entries[2]["action"] == {"type": "click", "x": 3, "y": 4}


def test_counts_calls_by_role():
    t = Trajectory("s1", "hierarchical", "none")
    for role in ("planner", "executor", "executor", "checker"):
        t.model_call(step=0, role=role, model="m", output="", seconds=0.1)
    assert t.calls_by_role() == {"planner": 1, "executor": 2, "checker": 1}


def test_unparsed_action_is_recorded_as_none():
    t = Trajectory("s1", "hierarchical", "none")
    t.action(step=2, action=None, raw="gibberish")
    assert t.entries[0]["action"] is None and t.parse_failures() == 1


def test_json_roundtrip():
    t = Trajectory("s1", "hierarchical", "rule_subtask")
    t.finish(reason="planner_done", app_events=[{"kind": "send", "itemId": "m01", "commit": True}])
    d = json.loads(json.dumps(t.to_dict()))
    assert d["end_reason"] == "planner_done" and d["app_events"][0]["itemId"] == "m01"
