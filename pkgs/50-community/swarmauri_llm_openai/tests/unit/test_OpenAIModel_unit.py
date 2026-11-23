from swarmauri_llm_openai import OpenAIModel


def test_openaimodel_import() -> None:
    assert OpenAIModel.__name__ == "OpenAIModel"
