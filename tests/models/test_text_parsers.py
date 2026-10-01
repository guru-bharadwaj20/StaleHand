from stalehand.models.text_parsers import (parse_bound, parse_description, parse_rule, parse_subtask,
                                           parse_target, parse_verdict, same_target)


def test_subtask_line():
    assert parse_subtask("Thought...\nSubtask: Open the email titled Budget") == "Open the email titled Budget"


def test_subtask_done_marker():
    assert parse_subtask("Subtask: DONE") is None


def test_subtask_falls_back_to_first_line():
    assert parse_subtask("Open the email titled Budget\nmore") == "Open the email titled Budget"


def test_rule_fields():
    sub, rule = parse_rule("Target rule: the most recent email from Sam\nAction: open it and forward it")
    assert rule == "the most recent email from Sam"
    assert sub == "open it and forward it - the element that matches this rule: the most recent email from Sam"


def test_rule_without_action_field():
    sub, rule = parse_rule("Target rule: the cheapest cable")
    assert rule == "the cheapest cable" and sub.startswith("click it")


def test_verdicts():
    assert parse_verdict("Verdict: STALE\nReason: newer mail") == "STALE"
    assert parse_verdict("verdict: valid") == "VALID"
    assert parse_verdict("I am not sure") == "UNPARSED"


def test_description_from_click_call():
    assert parse_description('Thought: x\nAction: click("the email from Sam titled Budget")') == "the email from Sam titled Budget"
    assert parse_description("Action: the Send button") == "the Send button"


def test_rule_done_marker():
    assert parse_rule("Target rule: DONE") is None


def test_bound_fields():
    out = "Target rule: the cheapest kettle\nTarget: Prestige PKOSS 1.5L Kettle\nAction: open it and add it to the cart"
    assert parse_bound(out) == ("open it and add it to the cart - Prestige PKOSS 1.5L Kettle",
                                "the cheapest kettle", "Prestige PKOSS 1.5L Kettle", "open it and add it to the cart")


def test_bound_done_marker():
    assert parse_bound("Target rule: DONE") is None


def test_bound_without_target_is_unparsed():
    assert parse_bound("Target rule: the cheapest kettle\nAction: click it") is None


def test_resolved_target():
    assert parse_target('Target: "Q3 budget review"') == "Q3 budget review"
    assert parse_target("Target: NONE") is None
    assert parse_target("I cannot tell") is None


def test_same_target_ignores_case_quotes_and_punctuation():
    assert same_target("Q3 Budget Review.", "'q3 budget review'")
    assert not same_target("Q3 budget review", "Q4 budget review")


def test_empty_replies_count_as_done():
    assert parse_subtask("") is None and parse_subtask("  \n") is None
    assert parse_rule("") is None
