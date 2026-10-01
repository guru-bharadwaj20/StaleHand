import json

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


FIXTURE = json.loads((__import__("pathlib").Path(__file__).parents[1] / "schema" / "fixtures" / "job.json").read_text())


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
