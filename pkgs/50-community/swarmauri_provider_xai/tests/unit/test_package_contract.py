from importlib.metadata import entry_points, version

from swarmauri_provider_xai import XAIProvider


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_provider_xai")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.model_providers")
        if ep.name == "XAIProvider"
    )
    assert point.load() is XAIProvider
