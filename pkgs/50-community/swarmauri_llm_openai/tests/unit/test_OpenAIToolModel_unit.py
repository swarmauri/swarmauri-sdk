from swarmauri_llm_openai import OpenAIToolModel


def test_openaitoolmodel_import() -> None:
    assert OpenAIToolModel.__name__ == "OpenAIToolModel"
