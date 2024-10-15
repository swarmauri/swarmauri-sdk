import logging
import pytest
import os
from swarmauri.llms.concrete.OpenAIAudio import OpenAIAudio as LLM
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


@pytest.fixture(scope="module")
def openai_model():
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
def test_ubc_resource(openai_model):
    assert openai_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(openai_model):
    assert openai_model.type == "OpenAIAudio"


@pytest.mark.unit
def test_serialization(openai_model):
    assert openai_model.id == LLM.model_validate_json(openai_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(openai_model):
    assert openai_model.name == "whisper-1"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_transcription(openai_model, model_name):
    model = openai_model
    model.name = model_name

    prediction = model.predict(
        audio_path="pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3"
    )

    logging.info(prediction)

    assert type(prediction) is str


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_translation(openai_model, model_name):
    model = openai_model
    model.name = model_name

    prediction = model.predict(
        audio_path="pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3",
        task="translation",
    )

    logging.info(prediction)

    assert type(prediction) is str
