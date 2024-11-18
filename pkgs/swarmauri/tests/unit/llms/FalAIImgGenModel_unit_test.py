import pytest
import os
from swarmauri.llms.concrete.FalAIImgGenModel import FalAIImgGenModel
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("FAL_API_KEY")


@pytest.fixture(scope="module")
def fluxpro_imggen_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = FalAIImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = FalAIImgGenModel(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(fluxpro_imggen_model):
    assert fluxpro_imggen_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(fluxpro_imggen_model):
    assert fluxpro_imggen_model.type == "FalAIImgGenModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(fluxpro_imggen_model):
    assert (
        fluxpro_imggen_model.id
        == FalAIImgGenModel.model_validate_json(
            fluxpro_imggen_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_model_name(fluxpro_imggen_model):
    assert fluxpro_imggen_model.name == "fal-ai/flux-pro"


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_generate_image(fluxpro_imggen_model, model_name):
    model = fluxpro_imggen_model
    model.name = model_name

    prompt = "A cute cat playing with a ball of yarn"
    image_url = model.generate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_agenerate_image(fluxpro_imggen_model, model_name):
    model = fluxpro_imggen_model
    model.name = model_name

    prompt = "A serene landscape with mountains and a lake"
    image_url = await model.agenerate_image(prompt=prompt)

    assert isinstance(image_url, str)
    assert image_url.startswith("http")


@timeout(5)
@pytest.mark.unit
def test_batch(fluxpro_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A steaming cup of coffee on a wooden table",
    ]

    image_urls = fluxpro_imggen_model.batch(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_abatch(fluxpro_imggen_model):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
        "A vintage car on a rural road",
    ]

    image_urls = await fluxpro_imggen_model.abatch(prompts=prompts)

    assert len(image_urls) == len(prompts)
    for url in image_urls:
        assert isinstance(url, str)
        assert url.startswith("http")
