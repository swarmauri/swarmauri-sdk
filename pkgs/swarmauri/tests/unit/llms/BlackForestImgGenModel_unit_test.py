import pytest
import os
from dotenv import load_dotenv
from swarmauri.llms.concrete.BlackForestImgGenModel import (
    BlackForestImgGenModel,
)

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("BLACKFOREST_API_KEY")


@pytest.fixture(scope="module")
def blackforest_imggen_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = BlackForestImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = BlackForestImgGenModel(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_model_resource(blackforest_imggen_model):
    assert blackforest_imggen_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_model_type(blackforest_imggen_model):
    assert blackforest_imggen_model.type == "BlackForestImgGenModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(blackforest_imggen_model):
    assert (
        blackforest_imggen_model.id
        == BlackForestImgGenModel.model_validate_json(
            blackforest_imggen_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_model_name(blackforest_imggen_model):
    assert blackforest_imggen_model.name == "flux-pro"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_generate_image(blackforest_imggen_model, model_name):
    model = blackforest_imggen_model
    model.name = model_name

    prompt = "A cute dog playing in a park"
    image_url = model.generate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_agenerate_image(blackforest_imggen_model, model_name):
    model = blackforest_imggen_model
    model.name = model_name

    prompt = "A mountain with snow and a river"
    image_url = await model.agenerate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@timeout(5)
@pytest.mark.unit
def test_batch_generate(blackforest_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A cup of coffee on a desk",
    ]

    image_urls = blackforest_imggen_model.batch_generate(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.unit
async def test_abatch_generate(blackforest_imggen_model):
    prompts = [
        "A space station in orbit",
        "A lion resting in the savannah",
        "A rainy day in a city",
    ]

    image_urls = await blackforest_imggen_model.abatch_generate(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")
