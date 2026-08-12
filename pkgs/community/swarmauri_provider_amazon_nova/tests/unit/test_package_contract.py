from importlib.metadata import entry_points, version

from swarmauri_provider_amazon_nova import AmazonNovaProvider


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_provider_amazon_nova")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.model_providers")
        if ep.name == "AmazonNovaProvider"
    )
    assert point.load() is AmazonNovaProvider
