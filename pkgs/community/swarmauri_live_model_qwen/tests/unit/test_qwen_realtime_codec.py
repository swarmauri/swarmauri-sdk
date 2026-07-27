import json
from swarmauri_live_model_qwen import QwenOmniRealtimeCodec


def test_text_delta():
    assert (
        QwenOmniRealtimeCodec()
        .decode(json.dumps({"type": "response.text.delta", "delta": "q"}))[0]
        .payload
        == "q"
    )
