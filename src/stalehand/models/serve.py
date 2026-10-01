"""A minimal OpenAI-compatible server around one local model, for boxes where vLLM is not installed.

Requests are answered one at a time with the same greedy decoding and prompt layout as the hf backend, so a run
through the server matches a run that loads the weights in-process. GET /v1/models also reports the weights'
revision, which the openai backend records in config.json.
"""
import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .base import Request


def request_from_body(body: dict) -> Request:
    """The single user message the openai backend sends: an optional image_url data URI and one text part."""
    (message,) = body["messages"]
    prompt, image = None, None
    for part in message["content"]:
        if part["type"] == "text":
            prompt = part["text"]
        elif part["type"] == "image_url":
            image = base64.b64decode(part["image_url"]["url"].split(",", 1)[1])
    if prompt is None:
        raise ValueError("no text part")
    return Request(prompt, image, int(body.get("max_tokens", 256)))


def make_server(model, host: str, port: int) -> ThreadingHTTPServer:
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, payload: dict) -> None:
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path.rstrip("/") != "/v1/models":
                return self._send(404, {"error": "not found"})
            self._send(200, {"object": "list", "data": [
                {"id": model.name, "object": "model", "revision": getattr(model, "revision", None)}]})

        def do_POST(self):
            if self.path.rstrip("/") != "/v1/chat/completions":
                return self._send(404, {"error": "not found"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                req = request_from_body(body)
            except (ValueError, KeyError, TypeError) as e:
                return self._send(400, {"error": f"bad request: {e}"})
            if body.get("model") != model.name:
                return self._send(404, {"error": f"this server has {model.name}, not {body.get('model')}"})
            with lock:
                text = model.generate([req])[0]
            self._send(200, {"object": "chat.completion", "model": model.name,
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                          "finish_reason": "stop"}]})

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer((host, port), Handler)
