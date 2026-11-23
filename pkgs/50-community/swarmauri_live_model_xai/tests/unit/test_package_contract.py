from importlib.metadata import entry_points, version

from swarmauri_live_model_xai import XAIRealtimeModel


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_live_model_xai")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.live_models")
        if ep.name == "XAIRealtimeModel"
    )
    assert point.load() is XAIRealtimeModel
