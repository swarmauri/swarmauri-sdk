import json

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.inputs.AudioInput import AudioInput
from swarmauri_base.live_models.inputs.TextInput import TextInput
from swarmauri_live_model_gemini import (
    GeminiLiveCodec,
    GeminiLiveConfigMapper,
    GeminiLiveToolAdapter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_helper_public_method_inventory_is_exhaustive():
    assert _public_methods(GeminiLiveConfigMapper) == {"map"}
    assert _public_methods(GeminiLiveCodec) == {"encode", "decode"}
    assert _public_methods(GeminiLiveToolAdapter) == {"result"}


def test_config_mapper_maps_model_modalities_and_overrides():
    mapped = GeminiLiveConfigMapper().map(
        "gemini-live",
        LiveConfigBase(
            requested_modalities=["audio"],
            provider_options={"setup": {"systemInstruction": "brief"}},
        ),
    )
    assert mapped["setup"]["model"] == "models/gemini-live"
    assert mapped["setup"]["generationConfig"]["responseModalities"] == [
        "AUDIO"
    ]
    assert mapped["setup"]["systemInstruction"] == "brief"


def test_codec_encodes_inputs_and_decodes_events():
    codec = GeminiLiveCodec()
    text = json.loads(codec.encode(TextInput(payload="hi")))
    audio = json.loads(codec.encode(AudioInput(payload=b"pcm")))
    events = codec.decode(
        json.dumps(
            {"serverContent": {"modelTurn": {"parts": [{"text": "hello"}]}}}
        )
    )
    assert text["realtimeInput"]["text"] == "hi"
    assert audio["realtimeInput"]["mediaChunks"][0]["data"] == "cGNt"
    assert events[0].payload == "hello"


def test_tool_adapter_preserves_tool_name_and_value():
    result = GeminiLiveToolAdapter().result("call-1", "weather", {"temp": 72})
    assert result.call_id == "call-1"
    assert result.correlation_id == "weather"
    assert result.payload == {"temp": 72}
