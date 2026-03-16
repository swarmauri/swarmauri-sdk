from swarmauri_llm_cohere import CohereModel


def test_coheremodel_import() -> None:
    assert CohereModel.__name__ == "CohereModel"
