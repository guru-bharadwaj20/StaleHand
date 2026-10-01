from stalehand.models.text_parsers import parse_description, parse_rule, parse_subtask, parse_verdict


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
