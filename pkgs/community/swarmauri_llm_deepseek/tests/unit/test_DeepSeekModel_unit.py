from swarmauri_llm_deepseek import DeepSeekModel


def test_deepseekmodel_import() -> None:
    assert DeepSeekModel.__name__ == "DeepSeekModel"
