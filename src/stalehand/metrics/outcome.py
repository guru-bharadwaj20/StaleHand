"""Score one episode: what did the agent commit to, and was the guard's firing warranted?

Outcomes:
  success       the committing action hit the correct target (and, for forward/reply, with the right details)
  stale         it hit the target the planner saw, which is no longer correct
  wrong_item    it hit some other item
  wrong_detail  right item, wrong recipient or wrong mode
  aborted       a guard stopped the episode before any commit
  no_commit     the episode ended without a commit

The correct target is the scenario's target after all its changes: changes land early (default step 1) and the
committing action comes later. `commit_before_change` flags episodes where the commit came first; their target
is then judged against the final screen, which the agent never saw, so analyses should report them separately.
"""
from typing import Any, Dict, List, Optional

FIRING = ("replan", "abort")


def _committing_event(scenario, events: List[dict]) -> Optional[dict]:
    action = scenario.meta.get("action")
    if action == "open":
        opens = [e for e in events if e.get("kind") == "open"]
        return opens[-1] if opens else None
    commits = [e for e in events if e.get("commit")]
    return commits[0] if commits else None


def _details_ok(scenario, event: dict) -> bool:
    action, detail = scenario.meta.get("action"), event.get("detail") or {}
    if action == "forward":
        return detail.get("mode") == "forward" and detail.get("to", "").strip() == scenario.meta.get("recipient")
    if action == "reply":
        return detail.get("mode") == "reply"
    return True


def score(scenario, trajectory) -> Dict[str, Any]:
    events = trajectory.app_events
    final = scenario.target_at(scenario.last_change_step)
    stale = scenario.stale_target
    event = _committing_event(scenario, events)
    if event is None:
        outcome = "aborted" if trajectory.end_reason == "guard_abort" else "no_commit"
        target = None
    else:
        target = event.get("itemId")
        if target == final:
            outcome = "success" if _details_ok(scenario, event) else "wrong_detail"
        elif target == stale:
            outcome = "stale"
        else:
            outcome = "wrong_item"

    change_step = scenario.changes[0].step if scenario.changes else None
    fired_steps = [e["step"] for e in trajectory.entries if e["kind"] == "decision" and e["decision"] in FIRING]
    if scenario.change_kind in ("relevant", "target_removed"):
        false_alarm = any(s < change_step for s in fired_steps)
    else:
        false_alarm = bool(fired_steps)

    calls = trajectory.calls_by_role()
    steps = [e["step"] for e in trajectory.entries if e["kind"] == "action" and e["action"] is not None
             and e["action"].get("type") != "done"]
    return {
        "scenario_id": scenario.id, "guard": trajectory.guard, "architecture": trajectory.architecture,
        "kind": scenario.meta.get("kind"), "variant": scenario.meta.get("variant"),
        "change_kind": scenario.change_kind, "outcome": outcome, "target": target,
        "correct_target": final, "stale_target": stale, "end_reason": trajectory.end_reason,
        "fired": len(fired_steps), "false_alarm": false_alarm,
        "planner_calls": calls.get("planner", 0), "executor_calls": calls.get("executor", 0),
        "checker_calls": calls.get("checker", 0),
        "model_seconds": round(sum(e["seconds"] for e in trajectory.entries if e["kind"] == "model_call"), 4),
        "env_steps": len(steps), "parse_failures": trajectory.parse_failures(),
        "commit_step": None if event is None else event.get("step"),
        "commit_before_change": (event is not None and change_step is not None and event.get("step") is not None
                                 and event["step"] < change_step),
    }
