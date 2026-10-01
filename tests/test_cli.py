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
