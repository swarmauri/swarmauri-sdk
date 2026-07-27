from swarmauri_provider_openai import OpenAIProvider


def test_provider_defaults():
    provider = OpenAIProvider()
    assert provider.provider_name == "openai"
    assert provider.catalog.get_model("gpt-realtime")
