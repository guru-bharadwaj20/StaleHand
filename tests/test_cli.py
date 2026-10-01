import json
import os
import subprocess
import sys
from pathlib import Path

from stalehand.cli import main


def test_scenarios_command_writes_jsonl(tmp_path, capsys):
    out = tmp_path / "inbox.jsonl"
    assert main(["scenarios", "--domain", "inbox", "--n", "2", "--seed", "0", "--out", str(out)]) == 0
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert len(rows) == 2 * 2 * 5
    assert "20 scenarios" in capsys.readouterr().out


def test_scenarios_command_filters(tmp_path):
    out = tmp_path / "shop.jsonl"
    main(["scenarios", "--domain", "shop", "--n", "1", "--kinds", "cheapest", "--variants", "L1,L3", "--out", str(out)])
    assert len(out.read_text().splitlines()) == 2


def test_change_step_option(tmp_path):
    out = tmp_path / "s.jsonl"
    main(["scenarios", "--domain", "inbox", "--n", "1", "--variants", "L1", "--change-step", "3", "--out", str(out)])
    assert all(json.loads(l)["changes"][0]["step"] == 3 for l in out.read_text().splitlines())


FIXTURE = json.loads((Path(__file__).parents[1] / "schema" / "fixtures" / "job.json").read_text())


def test_run_job_passes_decoded_job_to_execute(tmp_path, monkeypatch):
    from stalehand.run import execute as ex
    seen = {}

    def fake(job, out_dir, root, load_model, make_env, backend):
        seen.update(job=job, out=out_dir, root=root, backend=backend)
        return 0
    monkeypatch.setattr(ex, "execute", fake)
    monkeypatch.setenv("STALEHAND_BACKEND", "openai")
    assert main(["run-job", "--job", FIXTURE["base64"], "--out", str(tmp_path / "o"), "--root", str(tmp_path)]) == 0
    assert seen["job"].id == FIXTURE["job"]["id"] and seen["backend"] == "openai"
    assert str(seen["out"]) == str(tmp_path / "o")


def test_run_job_rejects_a_bad_job(tmp_path, capsys):
    assert main(["run-job", "--job", "bm90IGpzb24=", "--out", str(tmp_path)]) == 2
    assert "bad job" in capsys.readouterr().err


def test_module_entry_point_runs_the_cli():
    src = str(Path(__file__).parents[1] / "src")
    r = subprocess.run([sys.executable, "-m", "stalehand", "--help"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": src})
    assert r.returncode == 0 and "run-job" in r.stdout


def test_serve_loads_the_named_model_and_listens(monkeypatch):
    from stalehand.models import hf, serve
    seen = {}

    class Fake:
        def __init__(self, model_id, batch):
            seen.update(model_id=model_id, batch=batch)

    class Server:
        def serve_forever(self):
            seen["served"] = True

    monkeypatch.setattr(hf, "HFVLM", Fake)
    monkeypatch.setattr(serve, "make_server",
                        lambda m, host, port, max_batch: seen.update(host=host, port=port) or Server())
    assert main(["serve", "--model", "ui-tars-1.5-7b", "--port", "8002"]) == 0
    assert seen == {"model_id": "ByteDance-Seed/UI-TARS-1.5-7B", "batch": 8, "host": "127.0.0.1", "port": 8002,
                    "served": True}


def test_report_command_writes_markdown(tmp_path, capsys):
    run = tmp_path / "runs" / "pilot" / "job1"
    run.mkdir(parents=True)
    rows = [{"scenario_id": "shop-cheapest-000-L1", "guard": g, "outcome": o, "change_kind": "relevant",
             "kind": "cheapest", "false_alarm": False, "planner_calls": 1, "architecture": "hierarchical"}
            for g, o in (("none", "stale"), ("replan_every_step", "success"))]
    (run / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    out = tmp_path / "report.md"
    assert main(["report", "--runs", str(tmp_path / "runs"), "--out", str(out), "--n-boot", "100"]) == 0
    assert "Built from 2 scored episodes." in out.read_text()


def test_report_command_writes_charts_next_to_markdown(tmp_path):
    run = tmp_path / "runs" / "m" / "job1"
    run.mkdir(parents=True)
    rows = [{"scenario_id": "shop-cheapest-000-L1", "guard": g, "outcome": o, "change_kind": k,
             "kind": "cheapest", "false_alarm": False, "planner_calls": 1, "checker_calls": 0,
             "architecture": "hierarchical"}
            for g, o, k in (("none", "stale", "relevant"), ("none", "success", "none"))]
    (run / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    out = tmp_path / "main_report.md"
    assert main(["report", "--runs", str(tmp_path / "runs"), "--out", str(out), "--n-boot", "50", "--charts"]) == 0
    assert (tmp_path / "main_report_hierarchical_tradeoff.svg").exists()
    assert (tmp_path / "main_report_hierarchical_outcomes.svg").exists()
    assert "![" in out.read_text() and "main_report_hierarchical_tradeoff.svg" in out.read_text()
