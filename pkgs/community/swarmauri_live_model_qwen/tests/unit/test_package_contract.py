from importlib.metadata import entry_points, version

from swarmauri_live_model_qwen import QwenOmniRealtimeModel


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_live_model_qwen")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.live_models")
        if ep.name == "QwenOmniRealtimeModel"
    )
    assert point.load() is QwenOmniRealtimeModel
