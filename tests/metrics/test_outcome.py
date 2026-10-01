from stalehand.agents.trajectory import Trajectory
from stalehand.metrics.outcome import score
from stalehand.scenarios.domains import inbox, shop

REL = inbox.build(seed=0, kind="relative", index=0, variant="L1")   # target moves at step 1
FWD = next(inbox.build(seed=0, kind="relative", index=i, variant="L1") for i in range(50)
           if inbox.build(seed=0, kind="relative", index=i, variant="L1").meta["action"] == "forward")
SHOP = shop.build(seed=0, kind="cheapest", index=0, variant="L1")
NONE = shop.build(seed=0, kind="cheapest", index=0, variant="none")


def traj(events, decisions=(), reason="planner_done", calls=()):
    t = Trajectory("s", "hierarchical", "g")
    for step, role in calls:
        t.model_call(step=step, role=role, model="m", output="", seconds=0.5)
    for step, d in decisions:
        t.decision(step=step, guard="g", decision=d)
    t.finish(reason, events)
    return t


def commit(item, **detail):
    return {"kind": "add_to_cart", "itemId": item, "commit": True, "detail": detail}


def test_commit_on_final_target_is_success():
    final = SHOP.target_at(SHOP.last_change_step)
    assert score(SHOP, traj([commit(final)]))["outcome"] == "success"


def test_commit_on_stale_target_is_stale():
    assert score(SHOP, traj([commit(SHOP.stale_target)]))["outcome"] == "stale"


def test_commit_on_other_item_is_wrong_item():
    other = next(it.id for it in SHOP.items if it.id not in (SHOP.stale_target, SHOP.target_at(1)))
    assert score(SHOP, traj([commit(other)]))["outcome"] == "wrong_item"


def test_first_commit_counts():
    final = SHOP.target_at(1)
    assert score(SHOP, traj([commit(SHOP.stale_target), commit(final)]))["outcome"] == "stale"


def test_abort_without_commit():
    assert score(SHOP, traj([], reason="guard_abort"))["outcome"] == "aborted"


def test_no_commit():
    assert score(SHOP, traj([], reason="max_steps"))["outcome"] == "no_commit"


def test_forward_to_wrong_recipient_is_wrong_detail():
    final = FWD.target_at(1)
    ev = {"kind": "send", "itemId": final, "commit": True, "detail": {"mode": "forward", "to": "nobody@example.com"}}
    assert score(FWD, traj([ev]))["outcome"] == "wrong_detail"
    ev["detail"]["to"] = FWD.meta["recipient"]
    assert score(FWD, traj([ev]))["outcome"] == "success"


def test_open_task_uses_last_opened_mail():
    task = next(inbox.build(seed=0, kind="fixed", index=i, variant="none") for i in range(50)
                if inbox.build(seed=0, kind="fixed", index=i, variant="none").meta["action"] == "open")
    other = next(it.id for it in task.items if it.id != task.stale_target)
    events = [{"kind": "open", "itemId": other}, {"kind": "open", "itemId": task.stale_target}]
    assert score(task, traj(events))["outcome"] == "success"


def test_guard_firing_on_unchanged_screen_is_false_alarm():
    r = score(NONE, traj([], decisions=[(1, "replan")]))
    assert r["false_alarm"] and r["fired"] == 1


def test_guard_firing_after_relevant_change_is_not_false_alarm():
    r = score(SHOP, traj([], decisions=[(1, "replan")]))
    assert not r["false_alarm"]


def test_guard_firing_before_relevant_change_is_false_alarm():
    late = shop.build(seed=0, kind="cheapest", index=0, variant="L1", change_step=3)
    assert score(late, traj([], decisions=[(1, "abort")]))["false_alarm"]


def test_costs_are_counted():
    r = score(SHOP, traj([], calls=[(0, "planner"), (0, "executor"), (1, "executor"), (1, "checker")]))
    assert (r["planner_calls"], r["executor_calls"], r["checker_calls"]) == (1, 2, 1)
    assert r["model_seconds"] == 2.0


def test_commit_before_change_is_flagged():
    early = {"kind": "add_to_cart", "itemId": SHOP.stale_target, "commit": True, "step": 0}
    late = dict(early, step=4)
    assert score(SHOP, traj([early]))["commit_before_change"]
    assert not score(SHOP, traj([late]))["commit_before_change"]
