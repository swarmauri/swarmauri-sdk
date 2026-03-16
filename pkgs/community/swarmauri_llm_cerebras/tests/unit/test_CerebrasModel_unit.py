from swarmauri_llm_cerebras import CerebrasModel


def test_cerebrasmodel_import() -> None:
    assert CerebrasModel.__name__ == "CerebrasModel"
