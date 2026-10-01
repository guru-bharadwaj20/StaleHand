import pytest

from stalehand.models.base import Request, ScriptedVLM


def test_scripted_model_answers_by_first_matching_rule():
    m = ScriptedVLM([("Subgoal", "Subgoal: open the email"), ("", "Action: finished()")])
    out = m.generate([Request("Write the next Subgoal"), Request("anything else")])
    assert out == ["Subgoal: open the email", "Action: finished()"]


def test_scripted_model_records_requests():
    m = ScriptedVLM([("", "ok")])
    m.generate([Request("p", image_png=b"png")])
    assert m.calls[0].prompt == "p" and m.calls[0].image_png == b"png"


def test_scripted_model_without_match_fails_loudly():
    with pytest.raises(LookupError):
        ScriptedVLM([("never", "x")]).generate([Request("p")])


def test_callable_rule_gets_request():
    m = ScriptedVLM([(lambda r: r.max_new_tokens == 7, "seven")])
    assert m.generate([Request("p", max_new_tokens=7)]) == ["seven"]
