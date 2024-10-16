import pytest
import os
from swarmauri.llms.concrete.DeepInfraImgGenModel import DeepInfraImgGenModel
from dotenv import load_dotenv

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


@pytest.mark.unit
def test_ubc_resource(deepinfra_imggen_model):
    assert deepinfra_imggen_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(deepinfra_imggen_model):
    assert deepinfra_imggen_model.type == "DeepInfraImgGenModel"


@pytest.mark.unit
def test_serialization(deepinfra_imggen_model):
    assert (
        deepinfra_imggen_model.id
        == DeepInfraImgGenModel.model_validate_json(
            deepinfra_imggen_model.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_default_name(deepinfra_imggen_model):
    assert deepinfra_imggen_model.name == "stabilityai/stable-diffusion-2-1"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_generate_image(deepinfra_imggen_model, model_name, tmp_path):
    model = deepinfra_imggen_model
    model.name = model_name

    prompt = "A cute cat playing with a ball of yarn"
    save_path = tmp_path / "test_image.png"

    model.generate_image(prompt=prompt, save_path=str(save_path))

    assert save_path.exists()
    assert save_path.stat().st_size > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_agenerate_image(deepinfra_imggen_model, model_name, tmp_path):
    model = deepinfra_imggen_model
    model.name = model_name

    prompt = "A serene landscape with mountains and a lake"
    save_path = tmp_path / "test_async_image.png"

    await model.agenerate_image(prompt=prompt, save_path=str(save_path))

    assert save_path.exists()
    assert save_path.stat().st_size > 0


@pytest.mark.unit
def test_batch(deepinfra_imggen_model, tmp_path):
    prompts = [
        "A futuristic city skyline",
        "A tropical beach at sunset",
        "A steaming cup of coffee on a wooden table",
    ]
    save_paths = [str(tmp_path / f"batch_image_{i}.png") for i in range(len(prompts))]

    result_paths = deepinfra_imggen_model.batch(prompts=prompts, save_paths=save_paths)

    assert len(result_paths) == len(prompts)
    for path in result_paths:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_abatch(deepinfra_imggen_model, tmp_path):
    prompts = [
        "An abstract painting with vibrant colors",
        "A snowy mountain peak",
        "A vintage car on a rural road",
    ]
    save_paths = [
        str(tmp_path / f"async_batch_image_{i}.png") for i in range(len(prompts))
    ]

    result_paths = await deepinfra_imggen_model.abatch(
        prompts=prompts, save_paths=save_paths
    )

    assert len(result_paths) == len(prompts)
    for path in result_paths:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
