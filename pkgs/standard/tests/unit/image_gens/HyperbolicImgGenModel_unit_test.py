import pytest
import os
from swarmauri.image_gens.concrete.HyperbolicImgGenModel import HyperbolicImgGenModel
from dotenv import load_dotenv

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("HYPERBOLIC_API_KEY")


@pytest.fixture(scope="module")
def hyperbolic_imggen_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = HyperbolicImgGenModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = HyperbolicImgGenModel(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(hyperbolic_imggen_model):
    assert hyperbolic_imggen_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(hyperbolic_imggen_model):
    assert hyperbolic_imggen_model.type == "HyperbolicImgGenModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(hyperbolic_imggen_model):
    assert (
        hyperbolic_imggen_model.id
        == HyperbolicImgGenModel.model_validate_json(
            hyperbolic_imggen_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(hyperbolic_imggen_model):
    assert hyperbolic_imggen_model.name == "SDXL1.0-base"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_generate_image_base64(hyperbolic_imggen_model, model_name):
    model = hyperbolic_imggen_model
    model.name = model_name

    prompt = "A cute cat playing with a ball of yarn"

    image_base64 = model.generate_image_base64(prompt=prompt)

    assert isinstance(image_base64, str)
    assert len(image_base64) > 0


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_agenerate_image_base64(hyperbolic_imggen_model, model_name):
    model = hyperbolic_imggen_model
    model.name = model_name

    prompt = "A serene landscape with mountains and a lake"

    image_base64 = await model.agenerate_image_base64(prompt=prompt)

    assert isinstance(image_base64, str)
    assert len(image_base64) > 0


@timeout(5)
@pytest.mark.unit
def test_batch_base64(hyperbolic_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
    ]

    result_base64_images = hyperbolic_imggen_model.batch_base64(prompts=prompts)

    assert len(result_base64_images) == len(prompts)
    for image_base64 in result_base64_images:
        assert isinstance(image_base64, str)
        assert len(image_base64) > 0


@timeout(5)
@pytest.mark.asyncio
@pytest.mark.unit
async def test_abatch_base64(hyperbolic_imggen_model):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
    ]

    result_base64_images = await hyperbolic_imggen_model.abatch_base64(prompts=prompts)

    assert len(result_base64_images) == len(prompts)
    for image_base64 in result_base64_images:
        assert isinstance(image_base64, str)
        assert len(image_base64) > 0
