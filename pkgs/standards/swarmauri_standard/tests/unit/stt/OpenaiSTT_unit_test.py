import logging
import pytest
import os
from swarmauri_standard.stt.OpenaiSTT import OpenaiSTT
from dotenv import load_dotenv
from swarmauri_standard.utils.timeout_wrapper import timeout
from pathlib import Path

# Load environment variables
load_dotenv()

# Retrieve API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "test.mp3")
file_path2 = os.path.join(root_dir, "static", "test_fr.mp3")


@pytest.fixture(scope="module")
def openai_stt_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = OpenaiSTT(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = OpenaiSTT(api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(openai_stt_model):
    assert openai_stt_model.resource == "STT"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(openai_stt_model):
    assert openai_stt_model.type == "OpenaiSTT"


@timeout(5)
@pytest.mark.unit
def test_serialization(openai_stt_model):
    assert (
        openai_stt_model.id
        == OpenaiSTT.model_validate_json(openai_stt_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(openai_stt_model):
    assert openai_stt_model.name == openai_stt_model.allowed_models[0]


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_transcription(openai_stt_model, model_name):
    model = openai_stt_model
    model.name = model_name

    prediction = model.predict(audio_path=file_path)

    logging.info(prediction)

    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_translation(openai_stt_model, model_name):
    model = openai_stt_model
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
async def test_apredict(openai_stt_model, model_name):
    openai_stt_model.name = model_name

    prediction = await openai_stt_model.apredict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(openai_stt_model, model_name):
    model = openai_stt_model
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
async def test_abatch(openai_stt_model, model_name):
    model = openai_stt_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = await model.abatch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)
