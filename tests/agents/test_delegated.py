from stalehand.agents.delegated import Delegated
from stalehand.guards.base import Guard
from stalehand.scenarios.domains import inbox

from .fake_env import FakeEnv
from .test_hierarchical import CLICK, executor, planner

SCEN = inbox.build(seed=0, kind="relative", index=0, variant="L1")


def test_orchestrator_prompt_and_operator_reports():
    p = planner("forward the newest mail from Samuel Lee to laura@example.com")
    e = executor(CLICK, "Action: finished(content='forwarded it')")
    t = Delegated(p, e, Guard(), max_steps=10).run(FakeEnv(), SCEN)
    assert t.architecture == "delegated"
    assert p.calls[0].prompt.startswith("You are the orchestrator")
    assert "forward the newest mail from Samuel Lee to laura@example.com (operator report: forwarded it)" \
        in p.calls[1].prompt


def test_operator_hands_back_when_budget_runs_out():
    p = planner("do a long thing")
    e = executor(*[CLICK] * 6)
    t = Delegated(p, e, Guard(), max_steps=10, operator_budget=4).run(FakeEnv(), SCEN)
    subs = [x["step"] for x in t.entries if x["kind"] == "subtask"]
    assert subs == [0]
    assert "do a long thing (operator stopped: step budget of 4 used up)" in p.calls[1].prompt
    assert t.calls_by_role()["executor"] == 4


def test_rule_and_bound_guards_keep_their_own_planner_prompts():
    class RuleGuard(Guard):
        planner_mode = "rule"
    p = planner()
    Delegated(p, executor(), RuleGuard(), max_steps=3).run(FakeEnv(), SCEN)
    assert "Target rule" in p.calls[0].prompt
