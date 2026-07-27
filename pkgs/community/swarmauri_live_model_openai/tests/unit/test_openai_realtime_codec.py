import json

from swarmauri_live_model_openai import OpenAIRealtimeCodec


def test_text_delta():
    events = OpenAIRealtimeCodec().decode(
        json.dumps({"type": "response.output_text.delta", "delta": "hi"})
    )
    assert events[0].payload == "hi"
