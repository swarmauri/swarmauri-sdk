import logging
import pytest
import os
from swarmauri.llms.concrete.GroqAIAudio import GroqAIAudio as LLM
from swarmauri.utils.timeout_wrapper import timeout

API_KEY = os.getenv("GROQ_API_KEY")


@pytest.fixture(scope="module")
def groqai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_groqai_resource(groqai_model):
    assert groqai_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_groqai_type(groqai_model):
    assert groqai_model.type == "GroqAIAudio"


@timeout(5)
@pytest.mark.unit
def test_serialization(groqai_model):
    assert groqai_model.id == LLM.model_validate_json(groqai_model.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_default_name(groqai_model):
    assert groqai_model.name == "distil-whisper-large-v3-en"


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_audio_transcription(groqai_model, model_name):
    model = groqai_model
    model.name = model_name

    prediction = model.predict(
        audio_path="pkgs/swarmauri/tests/static/test.mp3",
    )

    logging.info(prediction)

    assert "this is a test audio file" in prediction.lower()
    assert type(prediction) is str


@timeout(5)
@pytest.mark.unit
def test_audio_translation(groqai_model):
    model = groqai_model
    model.name = "whisper-large-v3"

    prediction = model.predict(
        audio_path="pkgs/swarmauri/tests/static/test_fr.mp3",
        task="translation",
    )

    logging.info(prediction)

    assert "this is a test audio file" in prediction.lower()
    assert type(prediction) is str
