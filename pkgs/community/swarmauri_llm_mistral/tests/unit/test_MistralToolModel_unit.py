from swarmauri_llm_mistral import MistralToolModel


def test_mistraltoolmodel_import() -> None:
    assert MistralToolModel.__name__ == "MistralToolModel"
