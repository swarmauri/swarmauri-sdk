from importlib.metadata import entry_points, version

from swarmauri_provider_openai import OpenAIProvider


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_provider_openai")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.model_providers")
        if ep.name == "OpenAIProvider"
    )
    assert point.load() is OpenAIProvider
