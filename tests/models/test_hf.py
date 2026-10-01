import io

from PIL import Image

from stalehand.models.base import Request
from stalehand.models.hf import conversation


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
