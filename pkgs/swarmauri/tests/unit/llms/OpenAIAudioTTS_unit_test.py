# import io
import logging
import pytest
import os

# from pydub import AudioSegment
# from pydub.playback import play
from swarmauri.llms.concrete.OpenAIAudioTTS import OpenAIAudioTTS as LLM
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
file_path = "pkgs/swarmauri/tests/unit/llms/static/audio/test_tts.mp3"


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
    assert openai_model.type == "OpenAIAudioTTS"


@pytest.mark.unit
def test_serialization(openai_model):
    assert openai_model.id == LLM.model_validate_json(openai_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(openai_model):
    assert openai_model.name == "tts-1"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_predict(openai_model, model_name):
    openai_model.name = model_name

    text = "Hello, this is a test of streaming text-to-speech output."

    audio_file_path = openai_model.predict(text=text, audio_path=file_path)

    # audio_bytes.seek(0)
    # audio = AudioSegment.from_file(audio_bytes, format="mp3")
    # play(audio)

    logging.info(audio_file_path)

    assert isinstance(audio_file_path, str)


# New tests for streaming
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(openai_model, model_name):
    openai_model.name = model_name

    text = "Hello, this is a test of streaming text-to-speech output."

    collected_chunks = []
    for chunk in openai_model.stream(text=text):
        assert isinstance(chunk, bytes), f"is type is {type(chunk)}"
        collected_chunks.append(chunk)

    full_audio_byte = b"".join(collected_chunks)
    assert len(full_audio_byte) > 0

    assert isinstance(full_audio_byte, bytes), f"the type is {type(full_audio_byte)}"
    # audio = AudioSegment.from_file(io.BytesIO(full_audio_byte), format="mp3")
    # play(audio)


# New tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(openai_model, model_name):
    openai_model.name = model_name

    text = "Hello, this is a test of streaming text-to-speech output."

    audio_file_path = await openai_model.apredict(text=text, audio_path=file_path)

    # audio_bytes.seek(0)
    # audio = AudioSegment.from_file(audio_bytes, format="mp3")
    # play(audio)

    logging.info(audio_file_path)

    assert isinstance(audio_file_path, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(openai_model, model_name):
    openai_model.name = model_name

    text = "Hello, this is a test of streaming text-to-speech output."

    collected_chunks = []
    for chunk in openai_model.stream(text=text):
        assert isinstance(chunk, bytes), f"is type is {type(chunk)}"
        collected_chunks.append(chunk)

    full_audio_byte = b"".join(collected_chunks)
    assert len(full_audio_byte) > 0

    assert isinstance(full_audio_byte, bytes), f"the type is {type(full_audio_byte)}"
    # audio = AudioSegment.from_file(io.BytesIO(full_audio_byte), format="mp3")
    # play(audio)


# New tests for batch operations
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(openai_model, model_name):
    model = openai_model
    model.name = model_name

    file_path2 = "pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3"
    file_path3 = "pkgs/swarmauri/tests/unit/llms/static/audio/test_fr.mp3"

    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
        "Good morning": file_path3,
    }

    results = model.batch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)
    for result in results:
        assert isinstance(result, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(openai_model, model_name):
    model = openai_model
    model.name = model_name

    file_path2 = "pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3"
    file_path3 = "pkgs/swarmauri/tests/unit/llms/static/audio/test_fr.mp3"

    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
        "Good morning": file_path3,
    }

    results = await model.abatch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)
    for result in results:
        assert isinstance(result, str)
