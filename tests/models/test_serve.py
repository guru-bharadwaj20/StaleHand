import json
import threading
import urllib.error
import urllib.request

import pytest

from stalehand.models.base import Request
from stalehand.models.openai_compat import OpenAICompatVLM
from stalehand.models.serve import make_server

PNG = b"\x89PNG\r\n\x1a\nfake"


class Echo:
    name = "Qwen/Qwen3-VL-8B-Instruct"
    revision = "abc123"

    def __init__(self):
        self.seen = []

    def generate(self, requests):
        self.seen.extend(requests)
        return [f"{r.prompt}|{len(r.image_png or b'')}|{r.max_new_tokens}" for r in requests]


@pytest.fixture
def served():
    model = Echo()
    httpd = make_server(model, "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}/v1", model
    httpd.shutdown()
    httpd.server_close()


def test_round_trip_through_the_openai_client(served):
    url, model = served
    client = OpenAICompatVLM("Qwen/Qwen3-VL-8B-Instruct", base_url=url)
    assert client.generate([Request("click it", PNG, 64)]) == [f"click it|{len(PNG)}|64"]
    assert model.seen == [Request("click it", PNG, 64)]


def test_models_endpoint_reports_revision(served):
    url, _ = served
    with urllib.request.urlopen(f"{url}/models") as r:
        body = json.loads(r.read())
    assert body["data"] == [{"id": "Qwen/Qwen3-VL-8B-Instruct", "object": "model", "revision": "abc123"}]


def test_wrong_model_name_is_rejected(served):
    url, _ = served
    with pytest.raises(urllib.error.HTTPError) as e:
        OpenAICompatVLM("other/model", base_url=url).generate([Request("x")])
    assert e.value.code == 404


def test_malformed_body_is_a_400(served):
    url, _ = served
    req = urllib.request.Request(f"{url}/chat/completions", data=b"{not json", method="POST")
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req)
    assert e.value.code == 400
