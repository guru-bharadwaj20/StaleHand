import pytest

from stalehand.env.browser import BrowserEnv
from stalehand.scenarios.domains import inbox

pytestmark = pytest.mark.browser

S = inbox.build(seed=0, kind="relative", index=0, variant="L1", change_step=0)


def test_render_shows_the_planners_screen_and_the_changed_one():
    env = BrowserEnv(change_timing="after_handoff")
    try:
        planner_screen = env.reset(S).png
        env.handoff()
        changed_screen = env.observe().png
        assert env.render(S) == planner_screen
        assert env.render(S, through_step=0) == changed_screen
        assert env.step == 0 and env.scenario is S  # rendering leaves the live episode alone
    finally:
        env.close()


def test_render_can_outline_items():
    env = BrowserEnv()
    try:
        plain = env.render(S)
        outlined = env.render(S, outline={S.stale_target: "planner's target"})
        assert outlined != plain and outlined[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        env.close()


def test_render_command_writes_both_screens(tmp_path):
    from stalehand.cli import main
    from stalehand.scenarios.export import write_jsonl
    write_jsonl([S], tmp_path / "s.jsonl")
    assert main(["render", "--scenarios", str(tmp_path / "s.jsonl"), "--id", S.id, "--out-dir", str(tmp_path)]) == 0
    for name in ("planner", "changed"):
        assert (tmp_path / f"{S.id}-{name}.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
