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


def test_openai_client_reads_revision_from_server(served):
    url, _ = served
    assert OpenAICompatVLM("Qwen/Qwen3-VL-8B-Instruct", base_url=url).revision == "abc123"


def test_revision_is_none_when_server_does_not_say(server_without_revision):
    assert OpenAICompatVLM("m", base_url=server_without_revision).revision is None



class Plain:
    """Like vLLM: no revision to report."""
    name = "m"

    def generate(self, requests):
        return ["ok" for _ in requests]


@pytest.fixture
def server_without_revision():
    httpd = make_server(Plain(), "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}/v1"
    httpd.shutdown()
    httpd.server_close()


class Slow:
    """Records the size of every batch it is handed."""
    name = "m"

    def __init__(self, fail_batches_over=None):
        self.sizes, self.fail_over = [], fail_batches_over

    def generate(self, requests):
        import time
        if self.fail_over is not None and len(requests) > self.fail_over:
            raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")
        self.sizes.append(len(requests))
        time.sleep(0.05)
        return [r.prompt.upper() for r in requests]


def _fire(batcher, n):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(n) as pool:
        return list(pool.map(lambda i: batcher.submit(Request(f"p{i}")), range(n)))


def test_batcher_groups_concurrent_requests():
    from stalehand.models.serve import Batcher
    model = Slow()
    b = Batcher(model, max_batch=8, wait=0.05)
    assert _fire(b, 8) == [f"P{i}" for i in range(8)]
    assert sum(model.sizes) == 8 and max(model.sizes) > 1


def test_batcher_falls_back_to_single_requests_on_oom():
    from stalehand.models.serve import Batcher
    model = Slow(fail_batches_over=1)
    b = Batcher(model, max_batch=8, wait=0.05)
    assert _fire(b, 4) == ["P0", "P1", "P2", "P3"]
    assert set(model.sizes) == {1} and b.max_batch < 8


def test_batcher_passes_other_errors_to_the_caller():
    from stalehand.models.serve import Batcher

    class Broken:
        name = "m"

        def generate(self, requests):
            raise ValueError("bad image")
    with pytest.raises(ValueError, match="bad image"):
        Batcher(Broken(), max_batch=4, wait=0.01).submit(Request("x"))
