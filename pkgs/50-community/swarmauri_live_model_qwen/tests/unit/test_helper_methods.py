import json

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.inputs.AudioInput import AudioInput
from swarmauri_base.live_models.inputs.TextInput import TextInput
from swarmauri_live_model_qwen import (
    QwenOmniRealtimeCodec,
    QwenOmniRealtimeConfigMapper,
    QwenOmniRealtimeToolAdapter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_helper_public_method_inventory_is_exhaustive():
    assert _public_methods(QwenOmniRealtimeConfigMapper) == {"map"}
    assert _public_methods(QwenOmniRealtimeCodec) == {"encode", "decode"}
    assert _public_methods(QwenOmniRealtimeToolAdapter) == {"result"}


def test_config_mapper_maps_modalities_and_overrides():
    mapped = QwenOmniRealtimeConfigMapper().map(
        LiveConfigBase(
            requested_modalities=["text"],
            provider_options={"session": {"voice": "Cherry"}},
        )
    )
    assert mapped["session"]["modalities"] == ["text"]
    assert mapped["session"]["voice"] == "Cherry"


def test_codec_encodes_inputs_and_decodes_events():
    codec = QwenOmniRealtimeCodec()
    text = json.loads(codec.encode(TextInput(payload="hi")))
    audio = json.loads(codec.encode(AudioInput(payload=b"pcm")))
    events = codec.decode(
        json.dumps({"type": "response.text.delta", "delta": "hello"})
    )
    assert text["item"]["content"][0]["text"] == "hi"
    assert audio["audio"] == "cGNt"
    assert events[0].payload == "hello"


def test_tool_adapter_preserves_call_and_value():
    result = QwenOmniRealtimeToolAdapter().result("call-1", {"answer": 42})
    assert result.call_id == "call-1"
    assert result.payload == {"answer": 42}
