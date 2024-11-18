import pytest
import os
from dotenv import load_dotenv
from swarmauri.llms.concrete.OpenAIImgGenModel import OpenAIImgGenModel
from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


@pytest.fixture(scope="module")
def openai_image_model():
    if not API_KEY:
        pytest.skip("Skipping due to missing OPENAI_API_KEY environment variable")
    model = OpenAIImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = OpenAIImgGenModel(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(openai_image_model):
    assert openai_image_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(openai_image_model):
    assert openai_image_model.type == "OpenAIImgGenModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(openai_image_model):
    assert (
        openai_image_model.id
        == OpenAIImgGenModel.model_validate_json(
            openai_image_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_model_name(openai_image_model):
    assert openai_image_model.name == "dall-e-3"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.integration
def test_generate_image(openai_image_model, model_name):
    openai_image_model.name = model_name
    prompt = "A cute robot dog playing in a park"
    image_urls = openai_image_model.generate_image(prompt=prompt)

    assert isinstance(image_urls, list)
    assert len(image_urls) > 0
    assert all(isinstance(url, str) and url.startswith("http") for url in image_urls)


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.integration
async def test_agenerate_image(openai_image_model, model_name):
    openai_image_model.name = model_name
    prompt = "A futuristic cityscape with flying cars"
    image_urls = await openai_image_model.agenerate_image(prompt=prompt)

    assert isinstance(image_urls, list)
    assert len(image_urls) > 0
    assert all(isinstance(url, str) and url.startswith("http") for url in image_urls)


@pytest.mark.integration
def test_batch(openai_image_model):
    prompts = [
        "A serene mountain landscape",
        "A bustling city street at night",
        "An underwater scene with colorful fish",
    ]

    batch_results = openai_image_model.batch(prompts=prompts)

    assert len(batch_results) == len(prompts)
    for result in batch_results:
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(url, str) and url.startswith("http") for url in result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_abatch(openai_image_model):
    prompts = [
        "A magical forest with glowing mushrooms",
        "A steampunk-inspired flying machine",
        "A cozy cabin in the snow",
    ]

    batch_results = await openai_image_model.abatch(prompts=prompts)

    assert len(batch_results) == len(prompts)
    for result in batch_results:
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(url, str) and url.startswith("http") for url in result)


@timeout(5)
@pytest.mark.unit
def test_dall_e_3_single_image(openai_image_model):
    openai_image_model.name = "dall-e-3"
    prompt = "A surreal landscape with floating islands"
    image_urls = openai_image_model.generate_image(prompt=prompt)

    assert isinstance(image_urls, list)
    assert len(image_urls) == 1
    assert isinstance(image_urls[0], str) and image_urls[0].startswith("http")
