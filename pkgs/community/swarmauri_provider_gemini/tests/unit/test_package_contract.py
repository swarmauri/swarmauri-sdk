from importlib.metadata import entry_points, version

from swarmauri_provider_gemini import GeminiProvider


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_provider_gemini")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.model_providers")
        if ep.name == "GeminiProvider"
    )
    assert point.load() is GeminiProvider
