import logging
import pytest
import os
from swarmauri_standard.stt.GroqSTT import GroqSTT
from swarmauri_standard.utils.timeout_wrapper import timeout
from pathlib import Path

# Retrieve API key from environment variable
API_KEY = os.getenv("GROQ_API_KEY")

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "test.mp3")
file_path2 = os.path.join(root_dir, "static", "test_fr.mp3")


@pytest.fixture(scope="module")
def groq_stt_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqSTT(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = GroqSTT(api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(groq_stt_model):
    assert groq_stt_model.resource == "STT"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(groq_stt_model):
    assert groq_stt_model.type == "GroqSTT"


@timeout(5)
@pytest.mark.unit
def test_serialization(groq_stt_model):
    assert (
        groq_stt_model.id
        == GroqSTT.model_validate_json(groq_stt_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(groq_stt_model):
    assert groq_stt_model.name == groq_stt_model.allowed_models[0]


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_audio_transcription(groq_stt_model, model_name):
    model = groq_stt_model
    model.name = model_name

    prediction = model.predict(
        audio_path=file_path,
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.unit
def test_audio_translation(groq_stt_model):
    model = groq_stt_model
    model.name = "whisper-large-v3"

    prediction = model.predict(
        audio_path=file_path2,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(groq_stt_model, model_name):
    groq_stt_model.name = model_name

    prediction = await groq_stt_model.apredict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(groq_stt_model, model_name):
    model = groq_stt_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = model.batch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(groq_stt_model, model_name):
    model = groq_stt_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = await model.abatch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)
