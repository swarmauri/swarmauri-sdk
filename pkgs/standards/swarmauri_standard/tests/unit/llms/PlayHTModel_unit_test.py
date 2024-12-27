import logging
import pytest
import os

from swarmauri.llms.concrete.PlayHTModel import PlayHTModel as LLM
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout
from pathlib import Path


# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "test.mp3")
file_path2 = os.path.join(root_dir, "static", "test_fr.mp3")


load_dotenv()

API_KEY = os.getenv("PlayHT_API_KEY")
USER_ID = os.getenv("PlayHT_USER_ID")


@pytest.fixture(scope="module")
def playht_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(user_id=USER_ID, api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(user_id=USER_ID, api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(playht_model):
    assert playht_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(playht_model):
    assert playht_model.type == "PlayHTModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(playht_model):
    assert playht_model.id == LLM.model_validate_json(playht_model.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_default_name(playht_model):
    assert playht_model.name == "Play3.0-mini"


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_predict(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    audio_path = playht_model.predict(text=text, audio_path=file_path)

    logging.info(audio_path)

    assert isinstance(audio_path, str)


# New tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_apredict(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    audio_file_path = await playht_model.apredict(text=text, audio_path=file_path)

    logging.info(audio_file_path)

    assert isinstance(audio_file_path, str)


# New tests for batch operations
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_batch(playht_model, model_name):
    model = playht_model
    model.name = model_name

    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
    }

    results = model.batch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)
    for result in results:
        assert isinstance(result, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_abatch(playht_model, model_name):
    model = playht_model
    model.name = model_name

    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
    }

    results = await model.abatch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)
    for result in results:
        assert isinstance(result, str)


@timeout(5)
@pytest.mark.unit
def test_create_cloned_voice_with_file(playht_model):
    voice_name = "test-voice"

    response = playht_model.clone_voice_from_file(voice_name, file_path)

    assert response is not None
    assert "id" in response or "error" not in response


@timeout(5)
@pytest.mark.unit
def test_create_cloned_voice_with_url(playht_model):
    sample_file_url = "https://drive.google.com/file/d/1JUzRWEu0iDl9gVKthOg2z3ENkx_dya5y/view?usp=sharing"
    voice_name = "mikel-voice"

    response = playht_model.clone_voice_from_url(sample_file_url, voice_name)

    assert response is not None
    assert "id" in response or "error" not in response


@timeout(5)
@pytest.mark.unit
def test_delete_cloned_voice(playht_model):
    cloned_voices = playht_model.get_cloned_voices()
    if cloned_voices:
        voice_id = cloned_voices[0].get("id")

        response = playht_model.delete_cloned_voice(voice_id)

        assert response is not None
        assert (
            response.get("message") == "Voice deleted successfully"
            or "error" not in response
        )
    else:
        assert cloned_voices == []
