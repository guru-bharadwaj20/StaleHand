import json

import pytest

from stalehand.report.final import render, values


def write(root, name, rows, timing="after_handoff"):
    d = root / name / "job1"
    d.mkdir(parents=True)
    (d / "config.json").write_text(json.dumps({"job": {"change_timing": timing}}))
    (d / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def row(sid, guard, outcome, change_kind="relevant", arch="hierarchical", calls=2):
    return {"scenario_id": sid, "architecture": arch, "guard": guard, "outcome": outcome, "change_kind": change_kind,
            "kind": "fixed", "false_alarm": False, "planner_calls": calls, "checker_calls": 0}


def test_values_name_each_guard_metric_by_run_set(tmp_path):
    write(tmp_path, "main", [row("inbox-a-000-L1", "none", "stale"), row("inbox-a-000-none", "none", "success", "none"),
                             row("inbox-a-001-L1", "none", "success")])
    v = values(tmp_path, ["main"], n_boot=20)
    assert v["main.none.relevant_n"] == "2"
    assert v["main.none.relevant_stale"] == "50%"
    assert v["main.none.harmless_success"] == "100%"
    assert v["main.none.calls"] == "2.0"
    assert v["main.episodes"] == "3"


def test_values_include_paired_contrasts_against_main(tmp_path):
    write(tmp_path, "main", [row(f"shop-a-{i:03d}-L1", "none", "stale") for i in range(6)])
    write(tmp_path, "delegated", [row(f"shop-a-{i:03d}-L1", "none", "success", arch="delegated") for i in range(6)])
    v = values(tmp_path, ["main", "delegated"], n_boot=20)
    assert v["delegated.none.all.diff"] == "+100 pts"
    assert v["delegated.none.relevant.pairs"] == "6"
    assert "delegated.none.all.p_holm" in v and "delegated.none.all.ci" in v


def test_render_fills_placeholders_and_refuses_unknown_names():
    assert render("Stale {{a.b}} of the time.", {"a.b": "44%"}) == "Stale 44% of the time."
    with pytest.raises(KeyError, match="a.c"):
        render("{{a.c}}", {"a.b": "1"})


def test_values_pair_each_guard_against_none_inside_a_run_set(tmp_path):
    write(tmp_path, "domains_lab", [row(f"files-a-{i:03d}-L1", "none", "stale") for i in range(6)]
          + [row(f"files-a-{i:03d}-L1", "rebind_dom", "success") for i in range(6)])
    v = values(tmp_path, ["main", "domains_lab"], n_boot=20)
    assert v["domains_lab.rebind_dom.vs_none.diff"] == "+100 pts"
    assert v["domains_lab.rebind_dom.vs_none.pairs"] == "6"
