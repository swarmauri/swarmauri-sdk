from swarmauri_llm_anthropic import AnthropicModel


def test_anthropicmodel_import() -> None:
    assert AnthropicModel.__name__ == "AnthropicModel"
