import io

import pytest
from PIL import Image

from stalehand.guards import screendiff
from stalehand.guards.base import ABORT, PROCEED, REPLAN, Context
from stalehand.guards.pixel import PixelChange

needs_binary = pytest.mark.skipif(screendiff.binary() is None, reason="screendiff binary not built")


def png(colour, size=(64, 48), box=None):
    img = Image.new("RGB", size, colour)
    if box:
        img.paste((0, 0, 0), box)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@needs_binary
def test_compare_identical_screens():
    r = screendiff.compare(png("white"), png("white"))
    assert r["ssim"] == pytest.approx(1.0) and r["changed_fraction"] == 0


@needs_binary
def test_compare_reports_change():
    r = screendiff.compare(png("white"), png("white", box=(0, 0, 32, 48)))
    assert r["changed_fraction"] == pytest.approx(0.5)


def test_missing_binary_is_explained(monkeypatch):
    monkeypatch.setattr(screendiff, "binary", lambda: None)
    with pytest.raises(FileNotFoundError, match="cargo build"):
        screendiff.compare(b"", b"")


def ctx(old, new, step=1):
    return Context(env=None, task="t", subtask="s", subtask_step=0, subtask_png=old, step=step, png=new)


def test_pixel_guard_uses_threshold(monkeypatch):
    monkeypatch.setattr(screendiff, "compare", lambda a, b, region=None: {"ssim": 0.9, "changed_fraction": 0.2})
    assert PixelChange(threshold=0.1, on_change="abort").before_think(ctx(b"a", b"b")) == ABORT
    assert PixelChange(threshold=0.3, on_change="replan").before_think(ctx(b"a", b"b")) == PROCEED


def test_pixel_guard_skips_the_planner_screen(monkeypatch):
    monkeypatch.setattr(screendiff, "compare", lambda *a, **k: pytest.fail("should not compare"))
    assert PixelChange().before_think(ctx(b"a", b"a", step=0)) == PROCEED


def test_pixel_guard_name():
    assert PixelChange(threshold=0.05, on_change="replan").name == "pixel_0.05_replan"
