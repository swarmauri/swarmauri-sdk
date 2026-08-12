from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_live_model_amazon_nova import NovaSonicLiveModel
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            NovaSonicLiveModel,
            {},
            "LiveModel",
            "amazon.nova-sonic-v1:0",
            LiveModelBase,
            excluded_fields=("transport",),
        )
    ]
