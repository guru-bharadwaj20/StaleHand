import pytest

from stalehand.guards.base import ABORT, PROCEED, REPLAN, Context
from stalehand.guards.dom import DomChange
from tests.agents.fake_env import FakeEnv


def make(env, step, subtask_step=0):
    return Context(env=env, task="t", subtask="s", subtask_step=subtask_step, subtask_png=b"", step=step, png=b"")


def test_subtask_scope_fires_after_external_change():
    env = FakeEnv(external_at={2})
    g = DomChange(scope="subtask", on_change="abort")
    g.on_subtask(make(env, 0))
    env.act(None), env.act(None)
    assert g.before_think(make(env, 2)) == ABORT


def test_subtask_scope_ignores_quiet_screens():
    env = FakeEnv()
    g = DomChange(scope="subtask", on_change="replan")
    g.on_subtask(make(env, 0))
    env.act(None)
    assert g.before_think(make(env, 1)) == PROCEED


def test_step_scope_checks_between_screenshot_and_action():
    env = FakeEnv()
    g = DomChange(scope="step", on_change="replan")
    c = make(env, 0)
    assert g.before_think(c) == PROCEED  # marks
    env._external += 1                   # the page changes while the executor thinks
    assert g.before_act(c) == REPLAN


def test_names_describe_configuration():
    assert DomChange(scope="step", on_change="abort").name == "dom_step_abort"


def test_bad_configuration_is_rejected():
    with pytest.raises(ValueError):
        DomChange(scope="episode", on_change="abort")
