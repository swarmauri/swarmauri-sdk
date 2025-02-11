import pytest
import os
from swarmauri_standard.vcms.FalVCM import FalVCM
from dotenv import load_dotenv
from swarmauri_standard.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("FAL_API_KEY")


@pytest.fixture(scope="module")
def falai_vision_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = FalVCM(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = FalVCM(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(falai_vision_model):
    assert falai_vision_model.resource == "VCM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(falai_vision_model):
    assert falai_vision_model.type == "FalVCM"


@timeout(5)
@pytest.mark.unit
def test_serialization(falai_vision_model):
    assert (
        falai_vision_model.id
        == FalVCM.model_validate_json(falai_vision_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_model_name(falai_vision_model):
    assert falai_vision_model.name == "fal-ai/llava-next"


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_predict_vision(falai_vision_model, model_name):
    model = falai_vision_model
    model.name = model_name

    image_url = "https://llava-vl.github.io/static/images/monalisa.jpg"
    prompt = "Who painted this artwork?"
    result = model.predict_vision(image_url=image_url, prompt=prompt)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_apredict_vision(falai_vision_model, model_name):
    model = falai_vision_model
    model.name = model_name

    image_url = "https://llava-vl.github.io/static/images/monalisa.jpg"
    prompt = "Describe the woman in the painting."
    result = await model.apredict_vision(image_url=image_url, prompt=prompt)

    assert isinstance(result, str)
    assert len(result) > 0


@timeout(5)
@pytest.mark.unit
def test_batch(falai_vision_model):
    image_urls = [
        "https://llava-vl.github.io/static/images/monalisa.jpg",
        "https://llava-vl.github.io/static/images/monalisa.jpg",
    ]
    prompts = [
        "Who painted this artwork?",
        "Describe the woman in the painting.",
    ]

    results = falai_vision_model.batch(image_urls=image_urls, prompts=prompts)

    assert len(results) == len(image_urls)
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
@timeout(5)
@pytest.mark.unit
async def test_abatch(falai_vision_model):
    image_urls = [
        "https://llava-vl.github.io/static/images/monalisa.jpg",
        "https://llava-vl.github.io/static/images/monalisa.jpg",
    ]
    prompts = [
        "Who painted this artwork?",
        "Describe the woman in the painting.",
    ]

    results = await falai_vision_model.abatch(image_urls=image_urls, prompts=prompts)

    assert len(results) == len(image_urls)
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0
