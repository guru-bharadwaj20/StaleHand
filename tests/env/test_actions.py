import pytest

from stalehand.env.actions import Click, Done, Key, Scroll, Type, Wait, action_from_dict, action_to_dict


@pytest.mark.parametrize("action", [Click(10, 20), Type("hello"), Key("Enter"), Scroll(0, 300), Wait(), Done("ok")],
                         ids=lambda a: type(a).__name__)
def test_action_roundtrip(action):
    assert action_from_dict(action_to_dict(action)) == action


def test_click_rejects_negative_coordinates():
    with pytest.raises(ValueError):
        Click(-1, 5)


def test_unknown_action_is_rejected():
    with pytest.raises(ValueError):
        action_from_dict({"type": "teleport"})
