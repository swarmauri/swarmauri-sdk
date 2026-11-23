import json

from swarmauri_live_model_xai import XAIRealtimeCodec


def test_text_delta():
    assert (
        XAIRealtimeCodec()
        .decode(json.dumps({"type": "response.text.delta", "delta": "x"}))[0]
        .payload
        == "x"
    )
