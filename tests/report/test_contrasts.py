import json

from stalehand.report.contrasts import contrasts, load_runs, markdown


def row(sid, arch, guard, outcome, timing="after_handoff", change_kind="relevant"):
    return {"scenario_id": sid, "architecture": arch, "guard": guard, "outcome": outcome, "timing": timing,
            "change_kind": change_kind, "kind": "relative", "false_alarm": False, "planner_calls": 1}


def test_load_runs_tags_each_row_with_its_job_timing(tmp_path):
    for name, timing in (("a", "after_handoff"), ("b", "mid_step")):
        d = tmp_path / name
        d.mkdir()
        (d / "config.json").write_text(json.dumps({"job": {"change_timing": timing}}))
        (d / "results.jsonl").write_text(json.dumps(row("inbox-x-000-L1", "hierarchical", "none", "success")) + "\n")
    assert [r["timing"] for r in load_runs(tmp_path)] == ["after_handoff", "mid_step"]


def test_architectures_are_paired_within_guard_and_timing():
    rows = ([row(f"shop-c-{i:03d}-L1", "hierarchical", "none", "stale") for i in range(8)]
            + [row(f"shop-c-{i:03d}-L1", "delegated", "none", "success") for i in range(8)]
            + [row(f"shop-c-{i:03d}-L1", "delegated", "none", "success", timing="mid_step") for i in range(8)])
    out = contrasts(rows, axis="architecture", base="hierarchical", within=("guard", "timing"), n_boot=50)
    assert [(c["arm"], c["guard"], c["timing"], c["subset"], c["n"]) for c in out] == [
        ("delegated", "none", "after_handoff", "all", 8), ("delegated", "none", "after_handoff", "relevant", 8)]
    assert out[0]["diff"] == 1.0 and out[0]["a_only"] == 8


def test_holm_column_covers_every_comparison_in_the_table():
    rows = ([row(f"shop-c-{i:03d}-L1", "hierarchical", g, "stale") for i in range(8) for g in ("none", "x")]
            + [row(f"shop-c-{i:03d}-L1", "delegated", g, "success") for i in range(8) for g in ("none", "x")])
    out = contrasts(rows, axis="architecture", base="hierarchical", within=("guard", "timing"), n_boot=50)
    assert all(c["p_holm"] >= c["p"] for c in out) and len(out) == 4


def test_markdown_has_one_section_per_axis_and_skips_axes_without_pairs():
    rows = ([row(f"shop-c-{i:03d}-L1", "hierarchical", "none", "stale") for i in range(4)]
            + [row(f"shop-c-{i:03d}-L1", "hierarchical", "none", "success", timing="mid_step") for i in range(4)])
    md = markdown(rows, n_boot=50)
    assert "## Change timing: `mid_step` against `after_handoff`" in md
    assert "| hierarchical | none | all | 4 | 0% | 100% | +100 pts |" in md
    assert "## Architecture" not in md
