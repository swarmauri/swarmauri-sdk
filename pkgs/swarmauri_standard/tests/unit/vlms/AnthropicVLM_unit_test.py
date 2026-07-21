import pytest

from swarmauri_standard.vlms.AnthropicVLM import AnthropicVLM


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_anthropic_vlm_resource():
    model = AnthropicVLM(api_key="test")
    assert model.resource == "VLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_anthropic_vlm_type():
    model = AnthropicVLM(api_key="test")
    assert model.type == "AnthropicVLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_anthropic_vlm_serialization():
    model = AnthropicVLM(api_key="test")
    assert (
        model.id
        == AnthropicVLM.model_validate_json(model.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_anthropic_vlm_default_name():
    model = AnthropicVLM(api_key="test")
    assert model.name == model.allowed_models[0]


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_anthropic_vlm_has_vision_methods():
    model = AnthropicVLM(api_key="test")
    assert callable(model.predict_vision)
    assert callable(model.apredict_vision)
    assert callable(model.batch)
    assert callable(model.abatch)
    assert callable(model.stream)
    assert callable(model.astream)
