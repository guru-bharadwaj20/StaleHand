import pytest

from stalehand.models import registry
from stalehand.models.openai_compat import OpenAICompatVLM


def test_known_models_have_hf_ids_and_coordinate_modes():
    for name, spec in registry.MODELS.items():
        assert "/" in spec.hf_id and spec.coords in ("abs", "rel1000")


def test_openai_backend_uses_served_name():
    m = registry.load("ui-tars-1.5-7b", backend="openai", base_url="http://x/v1")
    assert isinstance(m, OpenAICompatVLM) and m.model == "ByteDance-Seed/UI-TARS-1.5-7B"


def test_unknown_model_or_backend():
    with pytest.raises(KeyError):
        registry.load("gpt-9")
    with pytest.raises(ValueError):
        registry.load("ui-tars-1.5-7b", backend="carrier-pigeon")
