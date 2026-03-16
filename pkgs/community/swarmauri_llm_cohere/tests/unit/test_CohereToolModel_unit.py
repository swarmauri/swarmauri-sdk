from swarmauri_llm_cohere import CohereToolModel


def test_coheretoolmodel_import() -> None:
    assert CohereToolModel.__name__ == "CohereToolModel"
