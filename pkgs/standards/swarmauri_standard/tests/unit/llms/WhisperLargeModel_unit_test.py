import logging
import pytest
import os
from swarmauri.llms.concrete.WhisperLargeModel import WhisperLargeModel as LLM
from swarmauri.utils.timeout_wrapper import timeout
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUGGINGFACE_TOKEN")

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "test.mp3")
file_path2 = os.path.join(root_dir, "static", "test_fr.mp3")


@pytest.fixture(scope="module")
def whisperlarge_model():
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
def test_ubc_resource(whisperlarge_model):
    assert whisperlarge_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(whisperlarge_model):
    assert whisperlarge_model.type == "WhisperLargeModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(whisperlarge_model):
    assert whisperlarge_model.id == LLM.model_validate_json(whisperlarge_model.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_default_name(whisperlarge_model):
    assert whisperlarge_model.name == "openai/whisper-large-v3"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_transcription(whisperlarge_model, model_name):
    model = whisperlarge_model
    model.name = model_name

    prediction = model.predict(audio_path=file_path)

    logging.info(prediction)

    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_translation(whisperlarge_model, model_name):
    model = whisperlarge_model
    model.name = model_name

    prediction = model.predict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)

    assert type(prediction) is str


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(whisperlarge_model, model_name):
    whisperlarge_model.name = model_name

    prediction = await whisperlarge_model.apredict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(whisperlarge_model, model_name):
    model = whisperlarge_model
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
async def test_abatch(whisperlarge_model, model_name):
    model = whisperlarge_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = await model.abatch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)
