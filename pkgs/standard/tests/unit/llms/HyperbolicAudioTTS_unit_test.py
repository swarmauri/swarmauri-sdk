import logging
import pytest
import os

from swarmauri.llms.concrete.HyperbolicAudioTTS import HyperbolicAudioTTS as LLM
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout
from pathlib import Path

load_dotenv()

API_KEY = os.getenv("HYPERBOLIC_API_KEY")


# Get the current working directory
root_dir = Path(__file__).resolve().parents[2]

# Construct file paths dynamically
file_path = os.path.join(root_dir, "static", "hyperbolic_test_tts.mp3")
file_path2 = os.path.join(root_dir, "static", "hyperbolic_test2.mp3")
file_path3 = os.path.join(root_dir, "static", "hyperbolic_test3.mp3")


@pytest.fixture(scope="module")
def hyperbolic_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@timeout(5)
def get_allowed_languages():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_languages


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(hyperbolic_model):
    assert hyperbolic_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(hyperbolic_model):
    assert hyperbolic_model.type == "HyperbolicAudioTTS"


@timeout(5)
@pytest.mark.unit
def test_serialization(hyperbolic_model):
    assert (
        hyperbolic_model.id
        == LLM.model_validate_json(hyperbolic_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_speed(hyperbolic_model):
    assert hyperbolic_model.speed == 1.0


@timeout(5)
@pytest.mark.parametrize("language", get_allowed_languages())
@pytest.mark.unit
def test_predict(hyperbolic_model, language):
    """
    Test prediction with different languages
    Note: Adjust the text according to the language if needed
    """
    # Set the language for the test
    hyperbolic_model.language = language

    # Select an appropriate text based on the language
    texts = {
        "EN": "Hello, this is a test of text-to-speech output in English.",
        "ES": "Hola, esta es una prueba de salida de texto a voz en español.",
        "FR": "Bonjour, ceci est un test de sortie de texte en français.",
        "ZH": "这是一个中文语音转换测试。",
        "JP": "これは日本語の音声合成テストです。",
        "KR": "이것은 한국어 음성 합성 테스트입니다.",
    }

    text = texts.get(
        language, "Hello, this is a generic test of text-to-speech output."
    )

    audio_file_path = hyperbolic_model.predict(text=text, audio_path=file_path)

    logging.info(audio_file_path)

    assert isinstance(audio_file_path, str)
    assert os.path.exists(audio_file_path)
    assert os.path.getsize(audio_file_path) > 0


@timeout(5)
@pytest.mark.unit
def test_batch(hyperbolic_model):
    """
    Test batch processing of multiple texts
    """
    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
        "Good morning": file_path3,
    }

    results = hyperbolic_model.batch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)

    for result in results:
        assert isinstance(result, str)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(hyperbolic_model):
    """
    Test asynchronous batch processing of multiple texts
    """
    text_path_dict = {
        "Hello": file_path,
        "Hi there": file_path2,
        "Good morning": file_path3,
    }

    results = await hyperbolic_model.abatch(text_path_dict=text_path_dict)
    assert len(results) == len(text_path_dict)

    for result in results:
        assert isinstance(result, str)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0
