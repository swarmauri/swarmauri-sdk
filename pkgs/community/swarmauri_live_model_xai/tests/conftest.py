from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_live_model_xai import XAIRealtimeModel
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            XAIRealtimeModel,
            {},
            "LiveModel",
            "grok-realtime",
            LiveModelBase,
            excluded_fields=("transport",),
        )
    ]
