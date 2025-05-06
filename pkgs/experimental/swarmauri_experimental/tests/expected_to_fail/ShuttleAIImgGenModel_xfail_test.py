import pytest
import os
from swarmauri_experimental.llms.ShuttleAIImgGenModel import ShuttleAIImgGenModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SHUTTLEAI_API_KEY")


@pytest.fixture(scope="module")
def shuttle_imggen_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = ShuttleAIImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = ShuttleAIImgGenModel(api_key=API_KEY)
    return model.allowed_models


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_generate_image(shuttle_imggen_model, model_name):
    model = shuttle_imggen_model
    model.model_name = model_name

    prompt = "A cute cat playing with a ball of yarn"
    image_url = model.generate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_agenerate_image(shuttle_imggen_model, model_name):
    model = shuttle_imggen_model
    model.model_name = model_name

    prompt = "A serene landscape with mountains and a lake"
    image_url = await model.agenerate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.unit
def test_batch(shuttle_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A steaming cup of coffee on a wooden table",
    ]

    image_urls = shuttle_imggen_model.batch(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.asyncio
@pytest.mark.unit
async def test_abatch(shuttle_imggen_model):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
        "A vintage car on a rural road",
    ]

    image_urls = await shuttle_imggen_model.abatch(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")
