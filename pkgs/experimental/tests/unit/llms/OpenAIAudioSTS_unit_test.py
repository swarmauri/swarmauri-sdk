import io
import logging
import pytest
import os
from swarmauri.llms.concrete.OpenAIAudioSTS import OpenAIAudioSTS as LLM
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


@pytest.fixture(scope="module")
def openai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(openai_model):
    assert openai_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(openai_model):
    assert openai_model.type == "OpenAIAudioSTS"


@pytest.mark.unit
def test_serialization(openai_model):
    assert openai_model.id == LLM.model_validate_json(openai_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(openai_model):
    assert openai_model.name == "gpt-3.5-turbo"
    assert openai_model.sst_model_name == "whisper-1"
    assert openai_model.tts_model_name == "tts-1"
    assert openai_model.tts_voice == "alloy"


@pytest.mark.unit
def test_predict(openai_model):
    input_file_path = "pkgs/swarmauri/tests/unit/llms/static/audio/test_tts.mp3"
    output_file_path = "pkgs/swarmauri/tests/unit/llms/static/audio/test.mp3"

    audio_output = openai_model.predict(
        audio_input_path=input_file_path, audio_output_path=output_file_path
    )

    # audio_bytes.seek(0)
    # audio = AudioSegment.from_file(audio_bytes, format="mp3")
    # play(audio)

    logging.info(audio_output)

    assert isinstance(audio_output, str)
