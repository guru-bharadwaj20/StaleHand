"""Backend for any OpenAI-compatible chat server (vLLM, SGLang, llama.cpp server). Stdlib only."""
import base64
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import List, Sequence

from .base import Request


class OpenAICompatVLM:
    def __init__(self, model: str, base_url: str = "http://127.0.0.1:8000/v1", workers: int = 8,
                 timeout: float = 300.0, api_key: str = "EMPTY", retry_seconds: float = 900.0,
                 retry_wait: float = 10.0):
        self.name, self.model, self.base_url = model, model, base_url.rstrip("/")
        self.workers, self.timeout, self.api_key = workers, timeout, api_key
        # a server that restarts (or a tunnel that drops) should pause episodes, not fail the job
        self.retry_seconds, self.retry_wait = retry_seconds, retry_wait

    @property
    def revision(self):
        """Weights revision as the server reports it under /v1/models (stalehand serve does; vLLM does not)."""
        try:
            with urllib.request.urlopen(f"{self.base_url}/models", timeout=30) as resp:
                listed = json.loads(resp.read()).get("data", [])
        except (OSError, ValueError):
            return None
        return next((m.get("revision") for m in listed if m.get("id") == self.model), None)

    def _body(self, r: Request) -> dict:
        content = []
        if r.image_png is not None:
            url = "data:image/png;base64," + base64.b64encode(r.image_png).decode()
            content.append({"type": "image_url", "image_url": {"url": url}})
        content.append({"type": "text", "text": r.prompt})
        return {"model": self.model, "messages": [{"role": "user", "content": content}],
                "temperature": 0, "max_tokens": r.max_new_tokens}

    def _one(self, r: Request) -> str:
        deadline = time.monotonic() + self.retry_seconds
        while True:
            try:
                return self._post(r)
            except urllib.error.HTTPError as e:
                if e.code < 500 or time.monotonic() >= deadline:
                    raise
            except OSError:  # refused, reset or timed out: the server or tunnel is down
                if time.monotonic() >= deadline:
                    raise
            time.sleep(self.retry_wait)

    def _post(self, r: Request) -> str:
        req = urllib.request.Request(f"{self.base_url}/chat/completions", data=json.dumps(self._body(r)).encode(),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]

    def generate(self, requests: Sequence[Request]) -> List[str]:
        with ThreadPoolExecutor(self.workers) as pool:
            return list(pool.map(self._one, requests))
