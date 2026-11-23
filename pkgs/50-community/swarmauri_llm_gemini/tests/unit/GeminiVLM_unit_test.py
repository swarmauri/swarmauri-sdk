import pytest

from swarmauri_llm_gemini.GeminiVLM import GeminiVLM


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_gemini_vlm_resource():
    model = GeminiVLM(api_key="test")
    assert model.resource == "VLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_gemini_vlm_type():
    model = GeminiVLM(api_key="test")
    assert model.type == "GeminiVLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_gemini_vlm_serialization():
    model = GeminiVLM(api_key="test")
    assert (
        model.id == GeminiVLM.model_validate_json(model.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_gemini_vlm_default_name():
    model = GeminiVLM(api_key="test")
    assert model.name == model.allowed_models[0]


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_gemini_vlm_has_vision_methods():
    model = GeminiVLM(api_key="test")
    assert callable(model.predict_vision)
    assert callable(model.apredict_vision)
    assert callable(model.batch)
    assert callable(model.abatch)
    assert callable(model.stream)
    assert callable(model.astream)
