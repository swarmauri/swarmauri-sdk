from swarmauri_llm_mistral import MistralModel


def test_mistralmodel_import() -> None:
    assert MistralModel.__name__ == "MistralModel"
