"""Short model names used in experiment matrices, mapped to weights and output conventions."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    hf_id: str
    coords: str = "abs"  # coordinate convention of emitted actions, for executors


MODELS = {
    "qwen3-vl-8b": ModelSpec("Qwen/Qwen3-VL-8B-Instruct", coords="rel1000"),
    "qwen3-vl-4b": ModelSpec("Qwen/Qwen3-VL-4B-Instruct", coords="rel1000"),
    "ui-tars-1.5-7b": ModelSpec("ByteDance-Seed/UI-TARS-1.5-7B", coords="abs"),
}


def load(name: str, backend: str = "hf", **kwargs):
    spec = MODELS[name]
    if backend == "hf":
        from .hf import HFVLM
        return HFVLM(spec.hf_id, **kwargs)
    if backend == "openai":
        from .openai_compat import OpenAICompatVLM
        return OpenAICompatVLM(spec.hf_id, **kwargs)
    raise ValueError(f"unknown backend {backend!r}")
