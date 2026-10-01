import xml.etree.ElementTree as ET

from stalehand.report.charts import relevant_outcomes, tradeoff


def row(guard, outcome, change_kind, false_alarm=False):
    return {"scenario_id": "s", "guard": guard, "outcome": outcome, "change_kind": change_kind, "kind": "k",
            "false_alarm": false_alarm, "planner_calls": 2, "checker_calls": 0, "architecture": "hierarchical"}


ROWS = [row("none", "stale", "relevant"), row("none", "success", "none"),
        row("rebind_dom", "success", "relevant"), row("rebind_dom", "success", "none", false_alarm=True)]


def test_tradeoff_is_valid_svg_with_one_dot_per_guard():
    svg = tradeoff(ROWS, "hierarchical", "Guards")
    root = ET.fromstring(svg)
    assert len(root.findall("{http://www.w3.org/2000/svg}circle")) == 2
    assert "rebind_dom (2.0 calls)" in svg and root.get("role") == "img"


def test_relevant_outcomes_orders_guards_by_success():
    svg = relevant_outcomes(ROWS, "hierarchical", "Outcomes")
    ET.fromstring(svg)
    assert svg.index("rebind_dom (n=1)") < svg.index("none (n=1)")
    assert "none: stale target 100%" in svg
