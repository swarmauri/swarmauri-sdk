from importlib.metadata import entry_points, version

from swarmauri_live_model_amazon_nova import NovaSonicLiveModel


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_live_model_amazon_nova")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.live_models")
        if ep.name == "NovaSonicLiveModel"
    )
    assert point.load() is NovaSonicLiveModel
