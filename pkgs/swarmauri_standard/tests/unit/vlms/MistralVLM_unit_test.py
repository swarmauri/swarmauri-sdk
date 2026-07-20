import pytest

from swarmauri_standard.vlms.MistralVLM import MistralVLM


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_mistral_vlm_resource():
    model = MistralVLM(api_key="test")
    assert model.resource == "VLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_mistral_vlm_type():
    model = MistralVLM(api_key="test")
    assert model.type == "MistralVLM"


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_mistral_vlm_serialization():
    model = MistralVLM(api_key="test")
    assert (
        model.id == MistralVLM.model_validate_json(model.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_mistral_vlm_default_name():
    model = MistralVLM(api_key="test")
    assert model.name == model.allowed_models[0]


@pytest.mark.unit
@pytest.mark.timeout(5)
def test_mistral_vlm_has_vision_methods():
    model = MistralVLM(api_key="test")
    assert callable(model.predict_vision)
    assert callable(model.apredict_vision)
    assert callable(model.batch)
    assert callable(model.abatch)
    assert callable(model.stream)
    assert callable(model.astream)
