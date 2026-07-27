from swarmauri_provider_gemini import GeminiProvider


def test_provider_defaults():
    provider = GeminiProvider()
    assert provider.provider_name == "gemini"
    assert provider.catalog.get_model("gemini-3.1-flash-live-preview")
