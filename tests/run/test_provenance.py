import subprocess

from stalehand.run.job import Job
from stalehand.run.provenance import config, git_state, model_info, versions

JOB = Job("83d285fd1485", "pilot", "scenarios/inbox_pilot.jsonl", "hierarchical", "dom_step_abort",
          "qwen3-vl-8b", "ui-tars-1.5-7b", 7, 12, "before_observation")


def test_git_state_reports_commit_and_dirty(tmp_path):
    run = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    run("init", "-q")
    (tmp_path / "f").write_text("a")
    run("add", "f")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    state = git_state(tmp_path)
    assert len(state["commit"]) == 40 and state["dirty"] is False
    (tmp_path / "f").write_text("b")
    assert git_state(tmp_path)["dirty"] is True


def test_git_state_outside_a_repo_is_none(tmp_path):
    assert git_state(tmp_path) is None


def test_versions_marks_missing_packages():
    v = versions(["pytest", "no-such-package-xyz"])
    assert v["pytest"] and v["no-such-package-xyz"] is None


class _Model:
    name = "Qwen/Qwen3-VL-8B-Instruct"
    revision = "abc123"


def test_model_info_keeps_name_and_revision():
    assert model_info("qwen3-vl-8b", _Model(), "hf") == {
        "name": "qwen3-vl-8b", "id": "Qwen/Qwen3-VL-8B-Instruct", "revision": "abc123", "backend": "hf"}


def test_model_info_without_revision():
    class M:
        name = "scripted"
    assert model_info("x", M(), "scripted")["revision"] is None


def test_config_holds_job_seed_and_environment(tmp_path):
    cfg = config(JOB, models={"planner": {"name": "p"}}, root=tmp_path)
    assert cfg["job"]["id"] == "83d285fd1485" and cfg["seed"] == 7
    assert cfg["models"]["planner"]["name"] == "p"
    assert cfg["git"] is None and "python" in cfg and "host" in cfg and "versions" in cfg
