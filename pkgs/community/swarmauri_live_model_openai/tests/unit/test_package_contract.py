from importlib.metadata import entry_points, version

from swarmauri_live_model_openai import (
    OpenAIRealtimeModel,
    OpenAIResponsesWSModel,
)


def test_distribution_and_entry_point_contract():
    assert version("swarmauri_live_model_openai")
    points = {
        ep.name: ep for ep in entry_points(group="swarmauri.live_models")
    }
    assert points["OpenAIRealtimeModel"].load() is OpenAIRealtimeModel
    assert points["OpenAIResponsesWSModel"].load() is OpenAIResponsesWSModel
