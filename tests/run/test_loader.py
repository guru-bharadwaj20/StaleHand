import pytest

from stalehand.models.openai_compat import OpenAICompatVLM
from stalehand.run.loader import model_loader


def test_openai_backend_routes_each_role_to_its_server():
    load = model_loader({"STALEHAND_BACKEND": "openai", "STALEHAND_PLANNER_URL": "http://a:8001/v1",
                         "STALEHAND_EXECUTOR_URL": "http://b:8002/v1"})
    p, e = load("qwen3-vl-8b", "planner"), load("ui-tars-1.5-7b", "executor")
    assert isinstance(p, OpenAICompatVLM) and p.base_url == "http://a:8001/v1"
    assert p.model == "Qwen/Qwen3-VL-8B-Instruct"
    assert e.base_url == "http://b:8002/v1" and e.model == "ByteDance-Seed/UI-TARS-1.5-7B"


def test_openai_backend_needs_a_url():
    with pytest.raises(KeyError, match="STALEHAND_EXECUTOR_URL"):
        model_loader({"STALEHAND_BACKEND": "openai"})("ui-tars-1.5-7b", "executor")


def test_hf_backend_loads_each_model_once():
    made = []
    load = model_loader({}, hf_factory=lambda hf_id: made.append(hf_id) or object())
    assert load("qwen3-vl-8b", "planner") is load("qwen3-vl-8b", "executor")
    assert made == ["Qwen/Qwen3-VL-8B-Instruct"]


def test_unknown_backend():
    with pytest.raises(ValueError, match="backend"):
        model_loader({"STALEHAND_BACKEND": "tpu"})
