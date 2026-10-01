import io

from PIL import Image

from stalehand.models.base import Request
from stalehand.models.hf import conversation, snapshot_revision


def png(w=4, h=3):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), "white").save(buf, format="PNG")
    return buf.getvalue()


def test_conversation_puts_text_before_image():
    conv = conversation(Request("look", image_png=png()))
    content = conv[0]["content"]
    assert conv[0]["role"] == "user" and [c["type"] for c in content] == ["text", "image"]
    assert content[1]["image"].size == (4, 3)


def test_text_only_conversation():
    assert [c["type"] for c in conversation(Request("hi"))[0]["content"]] == ["text"]


def test_snapshot_revision_from_hub_cache_path():
    path = "/hf/hub/models--Qwen--Qwen3-VL-8B-Instruct/snapshots/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b"
    assert snapshot_revision(path) == "0c351dd01ed87e9c1b53cbc748cba10e6187ff3b"


def test_snapshot_revision_of_plain_directory_is_none():
    assert snapshot_revision("/models/m_qwen8") is None
