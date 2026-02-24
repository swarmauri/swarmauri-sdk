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


@pytest.mark.unit
def test_ubc_resource(shuttle_imggen_model):
    assert shuttle_imggen_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(shuttle_imggen_model):
    assert shuttle_imggen_model.type == "ShuttleAIImgGenModel"


@pytest.mark.unit
def test_serialization(shuttle_imggen_model):
    assert (
        shuttle_imggen_model.id
        == ShuttleAIImgGenModel.model_validate_json(
            shuttle_imggen_model.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_default_model_name(shuttle_imggen_model):
    assert shuttle_imggen_model.model_name == "shuttleai/shuttle-2-diffusion"
