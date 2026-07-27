from swarmauri_provider_xai import XAIProvider


def test_provider_defaults():
    assert XAIProvider().provider_name == "xai"
