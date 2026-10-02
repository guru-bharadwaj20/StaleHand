import pytest

from stalehand.env.actions import Click, Done, Key, Scroll, Type, Wait
from stalehand.models.uitars import parse_action

SCREEN = (1288, 728)


def p(text, mode="abs"):
    return parse_action(text, SCREEN, mode)


def test_click_with_box_tokens():
    assert p("Thought: open it\nAction: click(start_box='<|box_start|>(640,140)<|box_end|>')") == Click(640, 140)


def test_click_plain_tuple():
    assert p("Action: click(start_box='(700,425)')") == Click(700, 425)


def test_click_point_tag():
    assert p("Action: click(point='<point>700 425</point>')") == Click(700, 425)


def test_double_and_right_click_are_clicks():
    assert p("Action: left_double(start_box='(10,20)')") == Click(10, 20)
    assert p("Action: right_single(start_box='(10,20)')") == Click(10, 20)


def test_relative_1000_coordinates_are_scaled():
    assert p("Action: click(start_box='(500,192)')", mode="rel1000") == Click(644, 140)


def test_box_with_four_numbers_uses_centre():
    assert p("Action: click(start_box='(100,100,200,200)')") == Click(150, 150)


def test_type_unescapes_content():
    assert p("Action: type(content='laura@example.com')") == Type("laura@example.com")
    assert p(r"Action: type(content='it\'s done')") == Type("it's done")


def test_type_with_trailing_newline_submits():
    assert p(r"Action: type(content='hello\n')") == Type("hello\n")


def test_hotkey_maps_to_playwright_names():
    assert p("Action: hotkey(key='enter')") == Key("Enter")
    assert p("Action: hotkey(key='ctrl c')") == Key("Control+c")


def test_scroll_direction():
    assert p("Action: scroll(start_box='(600,400)', direction='down')") == Scroll(0, 300)
    assert p("Action: scroll(start_box='(600,400)', direction='up')") == Scroll(0, -300)


def test_wait_and_finished():
    assert p("Action: wait()") == Wait()
    assert p("Action: finished(content='forwarded')") == Done("forwarded")


def test_unparseable_output_is_none():
    assert p("I think we should click the email") is None
    assert p("Action: click(start_box='')") is None


def test_last_action_line_wins():
    text = "Thought: earlier I wrote Action: wait()\nAction: click(start_box='(1,2)')"
    assert p(text) == Click(1, 2)


def test_clicks_are_clamped_to_screen():
    assert p("Action: click(start_box='(5000,-3)')") == Click(1287, 0)


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError):
        p("Action: click(start_box='(1,2)')", mode="pixels?")


def test_labelled_box_without_closing_quote_parses():
    # InternVL3.5 names the element, then gives its box on the 0-1000 grid, and drops the closing quote
    out = "Thought: open the Spam folder.\nAction: click(start_box='Spam[[23, 453, 150, 490]])"
    assert parse_action(out, (1288, 728), "rel1000") == Click(111, 343)


def test_digits_in_the_label_are_not_coordinates():
    out = "Action: click(start_box='8:37 AM[[944, 797, 980, 815]])"
    assert parse_action(out, (1288, 728), "rel1000") == Click(1239, 587)
