from stalehand.report.build import domain_of, markdown


def row(sid, guard, outcome, change_kind="relevant", kind="relative"):
    return {"scenario_id": sid, "guard": guard, "outcome": outcome, "change_kind": change_kind, "kind": kind,
            "false_alarm": False, "planner_calls": 1, "architecture": "hierarchical"}


ROWS = ([row(f"shop-cheapest-{i:03d}-L1", "none", "stale") for i in range(6)]
        + [row(f"shop-cheapest-{i:03d}-L1", "replan_every_step", "success") for i in range(6)]
        + [row("inbox-fixed-000-none", "none", "success", change_kind="none", kind="fixed"),
           row("inbox-fixed-000-none", "replan_every_step", "success", change_kind="none", kind="fixed")])


def test_domain_of():
    assert domain_of({"scenario_id": "inbox-fixed-000-none"}) == "inbox"


def test_markdown_has_rate_rows_and_paired_comparison():
    md = markdown(ROWS, n_boot=200)
    assert "| hierarchical | none | shop | relative | relevant | 6 | 0% | 100% |" in md
    assert "| hierarchical | replan_every_step | shop | relative | relevant | 6 | 100% | 0% |" in md
    # paired on relevant changes: replan_every_step wins all 6 discordant pairs
    assert "| hierarchical | replan_every_step | shop | 6 | 0% | 100% | +100 pts |" in md
    assert "p = 0.031" in md


def test_markdown_says_how_many_rows_it_read():
    assert "14 scored episodes" in markdown(ROWS, n_boot=50)


def test_arms_without_shared_scenarios_are_reported_not_fatal():
    rows = [row("shop-cheapest-000-L1", "none", "stale"), row("shop-cheapest-001-L1", "replan_every_step", "success")]
    md = markdown(rows, n_boot=50)
    assert "| hierarchical | replan_every_step | shop | 0 | no shared scenarios yet |" in md


def test_markdown_opens_with_guard_summary():
    md = markdown(ROWS, n_boot=50)
    assert md.index("## Summary by guard") < md.index("## Outcomes")
    assert "| hierarchical | none | 6 | 0% | 100% | 1 | 100% | 0% | 1.0 |" in md


def test_outcome_rows_are_ordered_baseline_first_then_by_name():
    rows = [row("shop-cheapest-000-L1", "rebind_dom", "success"), row("inbox-fixed-000-none", "none", "success"),
            row("shop-cheapest-000-L1", "none", "stale"), row("inbox-fixed-000-none", "rebind_dom", "success")]
    md = markdown(rows, n_boot=50)
    outcomes = md.split("## Outcomes")[1].split("##")[0]
    order = [line.split(" | ")[1:3] for line in outcomes.splitlines() if line.startswith("| hierarchical")]
    assert order == [["none", "inbox"], ["none", "shop"], ["rebind_dom", "inbox"], ["rebind_dom", "shop"]]


def test_tiny_p_values_are_not_printed_as_zero():
    rows = ([row(f"shop-cheapest-{i:03d}-L1", "none", "stale") for i in range(12)]
            + [row(f"shop-cheapest-{i:03d}-L1", "rebind_dom", "success") for i in range(12)])
    md = markdown(rows, n_boot=50)
    assert "p < 0.001" in md and "p = 0.000" not in md


def test_false_alarm_table_counts_harmless_episodes():
    md = markdown(ROWS, n_boot=50)
    assert "| hierarchical | none | 1 | 0% |" in md.split("## False alarms")[1]
