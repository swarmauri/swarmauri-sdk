import io
import logging
import pytest
import os

from pydub import AudioSegment
from pydub.playback import play
from swarmauri.llms.concrete.PlayHTModel import PlayHTModel as LLM
from dotenv import load_dotenv

file_path = "pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3"
file_path2 = "pkgs/swarmauri/tests/unit/llms/static/audio/test_fr.mp3"

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


@pytest.mark.unit
def test_ubc_resource(playht_model):
    assert playht_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(playht_model):
    assert playht_model.type == "PlayHTModel"


@pytest.mark.unit
def test_serialization(playht_model):
    assert playht_model.id == LLM.model_validate_json(playht_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(playht_model):
    assert playht_model.name == "Play3.0-mini"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_predict(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    audio_path = playht_model.predict(text=text, audio_path=file_path)

    logging.info(audio_path)

    assert isinstance(audio_path, str)


# New tests for streaming
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    collected_chunks = []
    for chunk in playht_model.stream(text=text):
        assert isinstance(chunk, bytes), f"is type is {type(chunk)}"
        collected_chunks.append(chunk)

    full_audio_byte = b"".join(collected_chunks)

    assert len(full_audio_byte) > 0

    assert isinstance(full_audio_byte, bytes), f"the type is {type(full_audio_byte)}"
    audio = AudioSegment.from_file(io.BytesIO(full_audio_byte), format="mp3")
    play(audio)


# New tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    audio_file_path = await playht_model.apredict(text=text, audio_path=file_path)

    logging.info(audio_file_path)

    assert isinstance(audio_file_path, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(playht_model, model_name):
    playht_model.name = model_name

    text = "Hello, My name is Michael, Am a Swarmauri Engineer"

    collected_chunks = []
    for chunk in playht_model.stream(text=text):
        assert isinstance(chunk, bytes), f"is type is {type(chunk)}"
        collected_chunks.append(chunk)

    full_audio_byte = b"".join(collected_chunks)
    assert len(full_audio_byte) > 0

    assert isinstance(full_audio_byte, bytes), f"the type is {type(full_audio_byte)}"


# New tests for batch operations
@pytest.mark.parametrize("model_name", get_allowed_models())
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
