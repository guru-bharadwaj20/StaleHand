import pytest

from stalehand.env.apps import app_url


def test_app_url_uses_env_dir(tmp_path, monkeypatch):
    (tmp_path / "inbox.html").write_text("<html></html>")
    monkeypatch.setenv("STALEHAND_APPS", str(tmp_path))
    assert app_url("inbox") == (tmp_path / "inbox.html").as_uri()


def test_missing_app_explains_how_to_build(tmp_path, monkeypatch):
    monkeypatch.setenv("STALEHAND_APPS", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="npm run build"):
        app_url("inbox")
