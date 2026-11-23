import json

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.inputs.AudioInput import AudioInput
from swarmauri_base.live_models.inputs.TextInput import TextInput
from swarmauri_live_model_openai import (
    OpenAIRealtimeCodec,
    OpenAIRealtimeConfigMapper,
    OpenAIRealtimeToolAdapter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_helper_public_method_inventory_is_exhaustive():
    assert _public_methods(OpenAIRealtimeConfigMapper) == {"map"}
    assert _public_methods(OpenAIRealtimeCodec) == {"encode", "decode"}
    assert _public_methods(OpenAIRealtimeToolAdapter) == {"result"}


def test_config_mapper_maps_modalities_and_provider_overrides():
    mapped = OpenAIRealtimeConfigMapper().map(
        LiveConfigBase(
            requested_modalities=["text"],
            provider_options={"session": {"voice": "alloy"}},
        )
    )
    assert mapped["session"]["output_modalities"] == ["text"]
    assert mapped["session"]["voice"] == "alloy"


def test_codec_encodes_inputs_and_decodes_events():
    codec = OpenAIRealtimeCodec()
    text_messages = [
        json.loads(item) for item in codec.encode(TextInput(payload="hi"))
    ]
    audio_message = json.loads(codec.encode(AudioInput(payload=b"pcm"))[0])
    events = codec.decode(
        json.dumps({"type": "response.output_text.delta", "delta": "hello"})
    )
    assert text_messages[0]["item"]["content"][0]["text"] == "hi"
    assert audio_message["audio"] == "cGNt"
    assert events[0].payload == "hello"


def test_tool_adapter_builds_error_result():
    result = OpenAIRealtimeToolAdapter().result(
        "call-1", {"answer": 42}, is_error=True
    )
    assert result.call_id == "call-1"
    assert result.payload == {"answer": 42}
    assert result.is_error is True
