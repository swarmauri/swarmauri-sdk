import logging
import pytest
import os
from swarmauri.llms.concrete.GroqAIAudio import GroqAIAudio as LLM
from swarmauri.utils.timeout_wrapper import timeout
from pathlib import Path

# Retrieve API key from environment variable
API_KEY = os.getenv("GROQ_API_KEY")

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "test.mp3")
file_path2 = os.path.join(root_dir, "static", "test_fr.mp3")


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
        audio_path=file_path,
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.unit
def test_audio_translation(groqai_model):
    model = groqai_model
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
async def test_apredict(groqai_model, model_name):
    groqai_model.name = model_name

    prediction = await groqai_model.apredict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(groqai_model, model_name):
    model = groqai_model
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
async def test_abatch(groqai_model, model_name):
    model = groqai_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = await model.abatch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)
