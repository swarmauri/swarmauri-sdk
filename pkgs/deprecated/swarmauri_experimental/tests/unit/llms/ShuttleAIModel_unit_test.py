import pytest
import os
from swarmauri_experimental.llms.ShuttleAIModel import ShuttleAIModel as LLM

from time import sleep
from dotenv import load_dotenv


def go_to_sleep():
    sleep(0.1)


load_dotenv()

API_KEY = os.getenv("SHUTTLEAI_API_KEY")


@pytest.fixture(scope="module")
def shuttleai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.mark.unit
def test_ubc_resource(shuttleai_model):
    assert shuttleai_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(shuttleai_model):
    assert shuttleai_model.type == "ShuttleAIModel"


@pytest.mark.unit
def test_serialization(shuttleai_model):
    assert (
        shuttleai_model.id
        == LLM.model_validate_json(shuttleai_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(shuttleai_model):
    assert shuttleai_model.name == "shuttleai/shuttle-3"
