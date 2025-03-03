import pytest
import os
from swarmauri_community.llms.concrete.LeptonAIImgGenModel import LeptonAIImgGenModel
from swarmauri.utils.timeout_wrapper import timeout
from dotenv import load_dotenv

load_dotenv()

LEPTON_API_KEY = os.getenv("LEPTON_API_KEY")


@pytest.fixture(scope="module")
def lepton_ai_imggen_model():
    if not LEPTON_API_KEY:
        pytest.skip("Skipping tests due to missing Lepton API key")
    model = LeptonAIImgGenModel(api_key=LEPTON_API_KEY)
    return model


def test_ubc_type(lepton_ai_imggen_model):
    assert lepton_ai_imggen_model.type == "LeptonAIImgGenModel"


def test_serialization(lepton_ai_imggen_model):
    assert (
        lepton_ai_imggen_model.id
        == LeptonAIImgGenModel.model_validate_json(
            lepton_ai_imggen_model.model_dump_json()
        ).id
    )


@timeout(5)
def test_generate_image(lepton_ai_imggen_model):
    prompt = "A cute cat playing with a ball of yarn"
    image_bytes = lepton_ai_imggen_model.generate_image(prompt=prompt)
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0


@timeout(5)
@pytest.mark.asyncio
async def test_agenerate_image(lepton_ai_imggen_model):
    prompt = "A serene landscape with mountains and a lake"
    image_bytes = await lepton_ai_imggen_model.agenerate_image(prompt=prompt)
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0


@timeout(5)
def test_batch(lepton_ai_imggen_model):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A steaming cup of coffee on a wooden table",
    ]
    result_image_bytes_list = lepton_ai_imggen_model.batch(prompts=prompts)
    assert len(result_image_bytes_list) == len(prompts)
    for image_bytes in result_image_bytes_list:
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0


@timeout(5)
@pytest.mark.asyncio
async def test_abatch(lepton_ai_imggen_model):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
        "A vintage car on a rural road",
    ]
    result_image_bytes_list = await lepton_ai_imggen_model.abatch(prompts=prompts)
    assert len(result_image_bytes_list) == len(prompts)
    for image_bytes in result_image_bytes_list:
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
