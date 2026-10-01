import pytest

from stalehand.guards import registry
from stalehand.models.base import ScriptedVLM


@pytest.mark.parametrize("name", ["none", "replan_every_step", "rule_subtask", "dom_step_abort",
                                  "dom_subtask_replan", "pixel_0.02_replan", "pixel_0.1_abort"])
def test_names_round_trip(name):
    assert registry.make(name).name == name


def test_self_check_needs_a_checker():
    with pytest.raises(ValueError):
        registry.make("self_check")
    assert registry.make("self_check", checker=ScriptedVLM([])).name == "self_check"


def test_unknown_guard():
    with pytest.raises(KeyError):
        registry.make("prayer")


@pytest.mark.parametrize("name", ["rebind_step", "rebind_dom"])
def test_rebind_guards_need_a_resolver(name):
    with pytest.raises(ValueError):
        registry.make(name)
    assert registry.make(name, checker=ScriptedVLM([])).name == name
