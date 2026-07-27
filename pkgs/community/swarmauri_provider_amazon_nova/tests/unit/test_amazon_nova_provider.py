from swarmauri_provider_amazon_nova import AmazonNovaProvider


def test_provider_defaults():
    provider = AmazonNovaProvider()
    assert provider.region == "us-east-1"
    assert provider.catalog.get_model("amazon.nova-sonic-v1:0")
