"""Pick how run-job reaches its models, from environment variables a host entry in hosts.json can set.

  STALEHAND_BACKEND        hf (default): load weights on this machine's GPU with transformers
                           openai: call OpenAI-compatible servers, possibly on other machines
  STALEHAND_PLANNER_URL    server for the planner (and the self-check guard), when the backend is openai
  STALEHAND_EXECUTOR_URL   server for the executor, when the backend is openai
"""
from typing import Callable, Mapping, Optional

from ..models.registry import MODELS

BACKENDS = ("hf", "openai")


def backend_of(environ: Mapping[str, str]) -> str:
    backend = environ.get("STALEHAND_BACKEND", "hf")
    if backend not in BACKENDS:
        raise ValueError(f"unknown backend {backend!r}; available: {BACKENDS}")
    return backend


def model_loader(environ: Mapping[str, str], hf_factory: Optional[Callable] = None) -> Callable[[str, str], object]:
    backend = backend_of(environ)
    if backend == "openai":
        from ..models.openai_compat import OpenAICompatVLM

        def load_remote(name: str, role: str):
            var = f"STALEHAND_{role.upper()}_URL"
            if var not in environ:
                raise KeyError(f"{var} must be set for the openai backend")
            return OpenAICompatVLM(MODELS[name].hf_id, base_url=environ[var])
        return load_remote

    if hf_factory is None:
        from ..models.hf import HFVLM
        hf_factory = HFVLM
    cache = {}

    def load_local(name: str, role: str):
        if name not in cache:  # one copy of the weights when the planner and executor are the same model
            cache[name] = hf_factory(MODELS[name].hf_id)
        return cache[name]
    return load_local
