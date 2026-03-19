from swarmauri_llm_openai import OpenAIAudio


def test_openaiaudio_import() -> None:
    assert OpenAIAudio.__name__ == "OpenAIAudio"
