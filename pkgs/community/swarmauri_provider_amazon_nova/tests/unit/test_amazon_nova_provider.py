from swarmauri_provider_amazon_nova import AmazonNovaProvider


def test_provider_defaults():
    provider = AmazonNovaProvider()
    assert provider.region == "us-east-1"
    assert provider.catalog.get_model("amazon.nova-sonic-v1:0")


def test_explicit_credentials_are_forwarded_but_not_serialized():
    provider = AmazonNovaProvider(
        access_key_id="access",
        secret_access_key="secret",
        session_token="token",
    )

    options = provider.connection_options()

    assert options["access_key_id"] == "access"
    assert options["secret_access_key"] == "secret"
    assert options["session_token"] == "token"
    dumped = provider.model_dump()
    assert "access_key_id" not in dumped
    assert "secret_access_key" not in dumped
    assert "session_token" not in dumped
