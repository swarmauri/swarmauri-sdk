import pytest

from swarmauri_llm_openai.OpenAIVLM import OpenAIVLM


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_openai_vlm_resource():
    model = OpenAIVLM(api_key="test")
    assert model.resource == "VLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_openai_vlm_type():
    model = OpenAIVLM(api_key="test")
    assert model.type == "OpenAIVLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_openai_vlm_serialization():
    model = OpenAIVLM(api_key="test")
    assert (
        model.id == OpenAIVLM.model_validate_json(model.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_openai_vlm_default_name():
    model = OpenAIVLM(api_key="test")
    assert model.name == model.allowed_models[0]


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_openai_vlm_has_vision_methods():
    model = OpenAIVLM(api_key="test")
    assert callable(model.predict_vision)
    assert callable(model.apredict_vision)
    assert callable(model.batch)
    assert callable(model.abatch)
    assert callable(model.stream)
    assert callable(model.astream)
