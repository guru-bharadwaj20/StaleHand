"""A minimal OpenAI-compatible server around one local model, for boxes where vLLM is not installed.

Requests that arrive together are run as one batch (greedy decoding, the hf backend's prompt layout, each reply cut
to its own token limit), so many parallel episodes share one GPU. A batch that runs out of GPU memory is retried one
request at a time and the batch limit is halved. GET /v1/models also reports the weights'
revision, which the openai backend records in config.json.
"""
import base64
import json
import queue
import threading
import time
from concurrent.futures import Future
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


def _is_oom(e: Exception) -> bool:
    return "out of memory" in str(e).lower()


class Batcher:
    """Collects requests for up to `wait` seconds (or max_batch of them) and runs them through the model together."""

    def __init__(self, model, max_batch: int = 8, wait: float = 0.02):
        self.model, self.max_batch, self.wait = model, max_batch, wait
        self.batches = 0
        self._q: "queue.Queue" = queue.Queue()
        threading.Thread(target=self._loop, daemon=True).start()

    def submit(self, req: Request) -> str:
        fut: Future = Future()
        self._q.put((req, fut))
        return fut.result()

    def _take(self):
        batch = [self._q.get()]
        deadline = time.monotonic() + self.wait
        while len(batch) < self.max_batch:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            try:
                batch.append(self._q.get(timeout=left))
            except queue.Empty:
                break
        return batch

    def _run(self, batch) -> None:
        try:
            outs = self.model.generate([r for r, _ in batch])
        except Exception as e:  # noqa: BLE001 - every caller must hear back
            if _is_oom(e) and len(batch) > 1:
                self.max_batch = max(1, self.max_batch // 2)
                self._free_cache()
                for item in batch:
                    self._run([item])
                return
            for _, fut in batch:
                fut.set_exception(e)
            return
        self.batches += 1
        for (_, fut), out in zip(batch, outs):
            fut.set_result(out)

    def _free_cache(self) -> None:
        torch = getattr(self.model, "_torch", None)
        if torch is not None:
            torch.cuda.empty_cache()

    def _loop(self) -> None:
        while True:
            self._run(self._take())


def make_server(model, host: str, port: int, max_batch: int = 8) -> ThreadingHTTPServer:
    batcher = Batcher(model, max_batch=max_batch)

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
            try:
                text = batcher.submit(req)
            except Exception as e:  # noqa: BLE001
                return self._send(500, {"error": f"generation failed: {e}"})
            self._send(200, {"object": "chat.completion", "model": model.name,
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                          "finish_reason": "stop"}]})

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer((host, port), Handler)
