from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_live_model_gemini import GeminiLiveModel
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            GeminiLiveModel,
            {},
            "LiveModel",
            "gemini-3.1-flash-live-preview",
            LiveModelBase,
            excluded_fields=("transport",),
        )
    ]
