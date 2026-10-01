import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from stalehand.models.base import Request
from stalehand.models.openai_compat import OpenAICompatVLM


@pytest.fixture
def server():
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append(body)
            text = body["messages"][0]["content"][-1]["text"]
            reply = {"choices": [{"message": {"content": f"echo: {text}"}}]}
            data = json.dumps(reply).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}/v1", seen
    httpd.shutdown()


def test_generate_returns_replies_in_order(server):
    url, _ = server
    m = OpenAICompatVLM("qwen", base_url=url, workers=4)
    assert m.generate([Request(f"p{i}") for i in range(6)]) == [f"echo: p{i}" for i in range(6)]


def test_request_is_greedy_and_carries_image(server):
    url, seen = server
    OpenAICompatVLM("qwen", base_url=url).generate([Request("look", image_png=b"\x89PNG", max_new_tokens=33)])
    body = seen[0]
    assert body["model"] == "qwen" and body["temperature"] == 0 and body["max_tokens"] == 33
    image = body["messages"][0]["content"][0]
    assert image["type"] == "image_url" and image["image_url"]["url"].startswith("data:image/png;base64,iVBORw")


def test_text_only_request_has_no_image(server):
    url, seen = server
    OpenAICompatVLM("qwen", base_url=url).generate([Request("hi")])
    assert [c["type"] for c in seen[0]["messages"][0]["content"]] == ["text"]
