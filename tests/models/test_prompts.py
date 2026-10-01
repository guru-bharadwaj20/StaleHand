import string

import pytest

from stalehand.models import prompts

FIELDS = {"PLANNER": {"task", "history"}, "RULE_PLANNER": {"task", "history"},
          "SELF_CHECK": {"task", "subtask"}, "EXECUTOR": {"instruction", "history"}}


@pytest.mark.parametrize("name", sorted(FIELDS))
def test_template_placeholders(name):
    tpl = getattr(prompts, name)
    found = {f for _, f, _, _ in string.Formatter().parse(tpl) if f}
    assert found == FIELDS[name]
    tpl.format(**{f: "x" for f in FIELDS[name]})
