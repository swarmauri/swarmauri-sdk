from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_live_model_openai import (
    OpenAIRealtimeModel,
    OpenAIResponsesWSModel,
)
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            OpenAIRealtimeModel,
            {},
            "LiveModel",
            "gpt-realtime",
            LiveModelBase,
            excluded_fields=("transport",),
        ),
        ComponentSpec(
            OpenAIResponsesWSModel,
            {},
            "LiveModel",
            "gpt-realtime",
            LiveModelBase,
            excluded_fields=("transport",),
        ),
    ]
