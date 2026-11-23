from importlib.metadata import entry_points, version

from swarmauri_provider_qwen import QwenProvider


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_provider_qwen")
    point = next(
        ep
        for ep in entry_points(group="swarmauri.model_providers")
        if ep.name == "QwenProvider"
    )
    assert point.load() is QwenProvider
