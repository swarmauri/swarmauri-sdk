from swarmauri_provider_xai import XAIProvider


def test_provider_defaults():
    assert XAIProvider().provider_name == "xai"


def test_authorized_config_does_not_serialize_key():
    provider = XAIProvider(api_key="secret")
    config = provider.connection_config("chat.completions", model="grok-4.3")

    assert config.endpoint == "https://api.x.ai/v1/chat/completions"
    assert provider.authorize(config)["Authorization"] == "Bearer secret"
    assert config.transport_options["model"] == "grok-4.3"
    assert "secret" not in provider.model_dump_json()
    assert "secret" not in config.model_dump_json()


def test_provider_rejects_unknown_capability():
    provider = XAIProvider()
    try:
        provider.connection_config("unknown")
    except ValueError as error:
        assert "unknown" in str(error)
    else:
        raise AssertionError("unknown xAI capability was accepted")
