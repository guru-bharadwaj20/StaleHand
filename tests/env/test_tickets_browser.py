import pytest

from stalehand.env.actions import Click, Type
from stalehand.scenarios.domains import tickets

pytestmark = pytest.mark.browser


def centre(box):
    x, y, w, h = box
    return Click(int(x + w / 2), int(y + h / 2))


def assign(env, item_id, to):
    env.act(centre(env.item_boxes()[item_id]))
    env.act(centre(env.role_box("assign")))
    env.act(centre(env.role_box("to")))
    env.act(Type(to))
    env.act(centre(env.role_box("save")))


def test_assign_is_a_commit_with_assignee(env):
    s = tickets.build(seed=0, kind="relative", index=0, variant="none")
    env.reset(s)
    assign(env, s.stale_target, s.meta["recipient"])
    commit = env.commits()[-1]
    assert commit["itemId"] == s.stale_target and commit["detail"]["to"] == s.meta["recipient"]


def test_escalation_lands_at_change_step(env):
    s = tickets.build(seed=0, kind="relative", index=0, variant="escalate", change_step=1)
    env.reset(s)
    env.act(Click(5, 5))
    assert s.target_at(1) != s.stale_target and s.target_at(1) in env.item_boxes()


def test_closed_ticket_cannot_be_assigned(env):
    s = tickets.build(seed=0, kind="fixed", index=0, variant="closed", change_step=3)
    env.reset(s)
    env.act(centre(env.item_boxes()[s.stale_target]))
    env.act(centre(env.role_box("assign")))
    env.act(centre(env.role_box("to")))  # step 3: the ticket closes under the form
    assert env.view()["name"] == "assign" and not env.commits()
