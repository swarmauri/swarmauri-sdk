import logging
import pytest
import os
from swarmauri.llms.concrete.OpenAIAudio import OpenAIAudio as LLM
from dotenv import load_dotenv

file_path = "pkgs/swarmauri/tests/static/test.mp3"
file_path2 = "pkgs/swarmauri/tests/static/test_fr.mp3"

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

    prediction = model.predict(audio_path=file_path)

    logging.info(prediction)

    assert type(prediction) is str


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_audio_translation(openai_model, model_name):
    model = openai_model
    model.name = model_name

    prediction = model.predict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)

    assert type(prediction) is str


# New tests for streaming
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(openai_model, model_name):
    openai_model.name = model_name

    collected_chunks = []
    for chunk in openai_model.predict(audio_path=file_path, task="translation"):
        assert isinstance(chunk, str)
        collected_chunks.append(chunk)

    full_text = "".join(collected_chunks)
    assert len(full_text) > 0

    assert isinstance(full_text, str)


# New tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(openai_model, model_name):
    openai_model.name = model_name

    prediction = openai_model.predict(
        audio_path=file_path,
        task="translation",
    )

    logging.info(prediction)
    assert type(prediction) is str


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(openai_model, model_name):
    openai_model.name = model_name

    collected_chunks = []
    async for chunk in openai_model.predict(audio_path=file_path, task="translation"):
        assert isinstance(chunk, str)
        collected_chunks.append(chunk)

    full_text = "".join(collected_chunks)
    assert len(full_text) > 0

    assert isinstance(full_text, str)


# New tests for batch operations
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(openai_model, model_name):
    model = openai_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = model.batch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(openai_model, model_name):
    model = openai_model
    model.name = model_name

    path_task_dict = {
        file_path: "translation",
        file_path2: "transcription",
    }

    results = await model.abatch(path_task_dict=path_task_dict)
    assert len(results) == len(path_task_dict)
    for result in results:
        assert isinstance(result, str)
