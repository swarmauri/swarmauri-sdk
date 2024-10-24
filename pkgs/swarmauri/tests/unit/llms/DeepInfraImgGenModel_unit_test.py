import pytest
import os
from swarmauri.llms.concrete.DeepInfraImgGenModel import DeepInfraImgGenModel
from dotenv import load_dotenv

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("DEEPINFRA_API_KEY")


@pytest.fixture(scope="module")
def deepinfra_imggen_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = DeepInfraImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = DeepInfraImgGenModel(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(deepinfra_imggen_model):
    assert deepinfra_imggen_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(deepinfra_imggen_model):
    assert deepinfra_imggen_model.type == "DeepInfraImgGenModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(deepinfra_imggen_model):
    assert (
        deepinfra_imggen_model.id
        == DeepInfraImgGenModel.model_validate_json(
            deepinfra_imggen_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(deepinfra_imggen_model):
    assert deepinfra_imggen_model.name == "stabilityai/stable-diffusion-2-1"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_generate_image_base64(deepinfra_imggen_model, model_name):
    model = deepinfra_imggen_model
    model.name = model_name

    prompt = "A cute cat playing with a ball of yarn"

    image_base64 = model.generate_image_base64(prompt=prompt)

    assert isinstance(image_base64, str)
    assert len(image_base64) > 0


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_agenerate_image_base64(deepinfra_imggen_model, model_name):
    model = deepinfra_imggen_model
    model.name = model_name

    prompt = "A serene landscape with mountains and a lake"

    image_base64 = await model.agenerate_image_base64(prompt=prompt)

    assert isinstance(image_base64, str)
    assert len(image_base64) > 0


@timeout(5)
@pytest.mark.unit
def test_batch_base64(deepinfra_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A steaming cup of coffee on a wooden table",
    ]

    result_base64_images = deepinfra_imggen_model.batch_base64(prompts=prompts)

    assert len(result_base64_images) == len(prompts)
    for image_base64 in result_base64_images:
        assert isinstance(image_base64, str)
        assert len(image_base64) > 0


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.unit
async def test_abatch_base64(deepinfra_imggen_model):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
        "A vintage car on a rural road",
    ]

    result_base64_images = await deepinfra_imggen_model.abatch_base64(prompts=prompts)

    assert len(result_base64_images) == len(prompts)
    for image_base64 in result_base64_images:
        assert isinstance(image_base64, str)
        assert len(image_base64) > 0
