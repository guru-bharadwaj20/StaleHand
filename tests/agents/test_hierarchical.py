from stalehand.agents.hierarchical import Hierarchical
from stalehand.guards.base import ABORT, PROCEED, REBIND, REPLAN, Guard
from stalehand.models.base import ScriptedVLM
from stalehand.scenarios.domains import inbox

from .fake_env import FakeEnv

SCEN = inbox.build(seed=0, kind="relative", index=0, variant="L1")


def planner(*subtasks):
    """Planner that hands out the given subtasks in order, then says DONE."""
    queue = list(subtasks)
    return ScriptedVLM([(lambda r: True, "")], name="planner") if not queue else _Seq(queue)


class _Seq(ScriptedVLM):
    def __init__(self, queue):
        super().__init__([], name="planner")
        self.queue = queue

    def generate(self, requests):
        self.calls.extend(requests)
        return [f"Subtask: {self.queue.pop(0)}" if self.queue else "Subtask: DONE" for _ in requests]


def executor(*outputs):
    seq = list(outputs)

    class E(ScriptedVLM):
        def generate(self, requests):
            self.calls.extend(requests)
            return [seq.pop(0) if seq else "Action: finished(content='')" for _ in requests]
    return E([], name="executor")


CLICK = "Action: click(start_box='(600,140)')"


def test_runs_subtasks_until_planner_is_done():
    env = FakeEnv(commit_on_click="m01")
    agent = Hierarchical(planner("open the mail", "forward it"), executor(CLICK, "Action: finished(content='')", CLICK),
                         Guard(), max_steps=10)
    t = agent.run(env, SCEN)
    assert t.end_reason == "planner_done"
    assert [e["text"] for e in t.entries if e["kind"] == "subtask"] == ["open the mail", "forward it"]
    assert t.calls_by_role() == {"planner": 3, "executor": 4}
    assert t.app_events[0]["itemId"] == "m01"


def test_stops_at_step_budget():
    env = FakeEnv()
    t = Hierarchical(planner("click forever"), executor(*[CLICK] * 50), Guard(), max_steps=4).run(env, SCEN)
    assert t.end_reason == "max_steps" and len(env.actions) == 4


def test_executor_sees_subtask_not_task():
    env = FakeEnv()
    ex = executor(CLICK)
    Hierarchical(planner("open the email titled Budget"), ex, Guard(), max_steps=1).run(env, SCEN)
    assert "open the email titled Budget" in ex.calls[0].prompt and SCEN.task not in ex.calls[0].prompt


def test_unparsed_output_becomes_wait():
    env = FakeEnv()
    t = Hierarchical(planner("x"), executor("no idea"), Guard(), max_steps=1).run(env, SCEN)
    assert t.parse_failures() == 1 and type(env.actions[0]).__name__ == "Wait"


class ReplanOnce(Guard):
    name = "replan_once"

    def __init__(self):
        self.fired = False

    def before_think(self, ctx):
        if ctx.step == 2 and not self.fired:
            self.fired = True
            return REPLAN
        return "proceed"


def test_replan_asks_planner_on_current_screen():
    env = FakeEnv()
    p = planner("first", "second")
    t = Hierarchical(p, executor(CLICK, CLICK, CLICK), ReplanOnce(), max_steps=3).run(env, SCEN)
    assert p.calls[1].image_png == b"screen-2"
    assert [e["text"] for e in t.entries if e["kind"] == "subtask"] == ["first", "second"]


class AbortAtAct(Guard):
    name = "abort"

    def before_act(self, ctx):
        return ABORT


def test_abort_ends_episode_before_acting():
    env = FakeEnv()
    t = Hierarchical(planner("x"), executor(CLICK), AbortAtAct(), max_steps=5).run(env, SCEN)
    assert t.end_reason == "guard_abort" and env.actions == [] and env.began == 1


def test_replans_are_bounded():
    class AlwaysReplan(Guard):
        def before_think(self, ctx):
            return REPLAN
    env = FakeEnv()
    t = Hierarchical(planner(*["again"] * 50), executor(), AlwaysReplan(), max_steps=5, max_replans=3).run(env, SCEN)
    assert t.end_reason == "max_replans"


def test_replanning_each_step_is_not_cut_short():
    from stalehand.guards.replan import ReplanEveryStep
    env = FakeEnv()
    t = Hierarchical(planner(*["click"] * 50), executor(*[CLICK] * 50), ReplanEveryStep(), max_steps=10,
                     max_replans=3).run(env, SCEN)
    assert t.end_reason == "max_steps" and len(env.actions) == 10


class _Mode(Guard):
    def __init__(self, mode):
        self.planner_mode, self.seen = mode, []

    def on_subtask(self, ctx):
        self.seen.append(dict(ctx.extra))


def test_bound_planner_gives_executor_the_target_and_guard_the_rule():
    replies = ["Target rule: newest mail from Samuel Lee\nTarget: Q3 budget review\nAction: open it",
               "Target rule: DONE"]
    p = ScriptedVLM([], name="planner")
    p.generate = lambda reqs: [replies.pop(0) for _ in reqs]
    guard = _Mode("bound")
    t = Hierarchical(p, executor("Action: finished(content='')"), guard, max_steps=5).run(FakeEnv(), SCEN)
    sub = [e for e in t.entries if e["kind"] == "subtask"]
    assert sub[0]["text"] == "open it - Q3 budget review" and sub[0]["rule"] == "newest mail from Samuel Lee"
    assert guard.seen == [{"rule": "newest mail from Samuel Lee", "target": "Q3 budget review", "action": "open it"}]


def test_rule_planner_passes_the_rule_to_the_guard():
    replies = ["Target rule: newest mail from Samuel Lee\nAction: open it", "Target rule: DONE"]
    p = ScriptedVLM([], name="planner")
    p.generate = lambda reqs: [replies.pop(0) for _ in reqs]
    guard = _Mode("rule")
    Hierarchical(p, executor("Action: finished(content='')"), guard, max_steps=5).run(FakeEnv(), SCEN)
    assert guard.seen == [{"rule": "newest mail from Samuel Lee"}]


class _RebindAtStep1(Guard):
    def before_think(self, ctx):
        if ctx.step == 1 and ctx.subtask == "open the mail":
            ctx.subtask = "open the other mail"
            return REBIND
        return PROCEED


def test_rebind_switches_subtask_without_calling_the_planner():
    p = planner("open the mail")
    e = executor("Action: wait()", "Action: finished(content='')")
    t = Hierarchical(p, e, _RebindAtStep1(), max_steps=5).run(FakeEnv(), SCEN)
    subs = [x for x in t.entries if x["kind"] == "subtask"]
    assert [s["text"] for s in subs] == ["open the mail", "open the other mail"]
    assert subs[1]["rebound"] is True and subs[1]["step"] == 1
    assert "open the other mail" in e.calls[1].prompt
    assert t.calls_by_role()["planner"] == 2  # the first subtask, then DONE; no extra planner call


def test_subtask_budget_returns_control_to_the_planner():
    class Budget2(Hierarchical):
        subtask_budget = 2

        def _report(self, subtask, message):
            return f"{subtask} [{'budget' if message is None else message}]"
    p = planner("keep clicking", "then stop")
    e = executor(CLICK, CLICK, CLICK, "Action: finished(content='ok')")
    t = Budget2(p, e, Guard(), max_steps=10).run(FakeEnv(), SCEN)
    subs = [(x["step"], x["text"]) for x in t.entries if x["kind"] == "subtask"]
    assert subs == [(0, "keep clicking"), (2, "then stop")]
    assert "keep clicking [budget]" in p.calls[1].prompt
    assert "then stop [ok]" in p.calls[2].prompt


def test_replan_to_the_same_subtask_keeps_executor_history():
    from stalehand.guards.replan import ReplanEveryStep
    p = planner("type the address", "type the address", "type the address", "send it")
    e = executor(CLICK, "Action: type(content='kenji@example.com')", "Action: finished(content='')",
                 "Action: finished(content='')")
    Hierarchical(p, e, ReplanEveryStep(), max_steps=6).run(FakeEnv(), SCEN)
    assert "1. Action: click" in e.calls[1].prompt  # same subtask after the re-plan: history survives
    assert "2. Action: type" in e.calls[2].prompt


def test_replan_to_a_new_subtask_clears_executor_history():
    from stalehand.guards.replan import ReplanEveryStep
    p = planner("open the mail", "forward it")
    e = executor(CLICK, "Action: finished(content='')", "Action: finished(content='')")
    Hierarchical(p, e, ReplanEveryStep(), max_steps=6).run(FakeEnv(), SCEN)
    assert "forward it" in e.calls[1].prompt and "1. Action" not in e.calls[1].prompt


def test_executor_sees_the_page_changed_at_handoff():
    p = planner("open the mail")
    e = executor("Action: finished(content='')")
    Hierarchical(p, e, Guard(), max_steps=5).run(FakeEnv(handoff_changes_at={0}), SCEN)
    assert p.calls[0].image_png == b"screen-0" and e.calls[0].image_png == b"screen-0-changed"


def test_replan_guard_reacts_to_a_handoff_change():
    from stalehand.guards.replan import ReplanEveryStep
    p = planner("open the mail", "open the newer mail")
    e = executor("Action: finished(content='')", "Action: finished(content='')")
    t = Hierarchical(p, e, ReplanEveryStep(), max_steps=5).run(FakeEnv(handoff_changes_at={0}), SCEN)
    assert p.calls[1].image_png == b"screen-0-changed"
    assert [x["text"] for x in t.entries if x["kind"] == "subtask"][:2] == ["open the mail", "open the newer mail"]
