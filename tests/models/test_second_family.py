"""The second executor family must load through the registry and its outputs must parse like the others."""
from stalehand.env.actions import Click
from stalehand.models import registry
from stalehand.models.openai_compat import OpenAICompatVLM
from stalehand.models.uitars import parse_action

SCREEN = (1288, 728)


def test_second_family_is_registered_with_a_different_publisher():
    spec = registry.MODELS["internvl3.5-8b"]
    first = registry.MODELS["ui-tars-1.5-7b"]
    assert spec.hf_id.split("/")[0] != first.hf_id.split("/")[0] and spec.coords == "rel1000"


def test_second_family_loads_on_the_openai_backend():
    m = registry.load("internvl3.5-8b", backend="openai", base_url="http://127.0.0.1:8001/v1")
    assert isinstance(m, OpenAICompatVLM) and m.model == "OpenGVLab/InternVL3_5-8B-HF"


def test_grid_point_maps_to_screen_pixels():
    out = "Thought: open it.\nAction: click(start_box='<|box_start|>(500,250)<|box_end|>')"
    assert parse_action(out, SCREEN, registry.MODELS["internvl3.5-8b"].coords) == Click(644, 182)


def test_grid_box_maps_to_its_centre():
    out = "Action: click(start_box='[[400,200,600,300]]')"
    assert parse_action(out, SCREEN, registry.MODELS["internvl3.5-8b"].coords) == Click(644, 182)
