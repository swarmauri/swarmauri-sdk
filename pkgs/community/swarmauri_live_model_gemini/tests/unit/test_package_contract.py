from importlib.metadata import entry_points, version

from swarmauri_live_model_gemini import GeminiLiveModel


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_live_model_gemini")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.live_models")
        if ep.name == "GeminiLiveModel"
    )
    assert point.load() is GeminiLiveModel
