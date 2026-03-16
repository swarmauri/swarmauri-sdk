from swarmauri_llm_llamacpp import LlamaCppModel


def test_llamacppmodel_import() -> None:
    assert LlamaCppModel.__name__ == "LlamaCppModel"
