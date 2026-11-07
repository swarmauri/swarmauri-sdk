import base64

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.inputs.AudioInput import AudioInput
from swarmauri_base.live_models.inputs.TextInput import TextInput
from swarmauri_live_model_amazon_nova import (
    NovaSonicCodec,
    NovaSonicConfigMapper,
    NovaSonicToolAdapter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_helper_public_method_inventory_is_exhaustive():
    assert _public_methods(NovaSonicConfigMapper) == {"map"}
    assert _public_methods(NovaSonicCodec) == {"encode", "decode"}
    assert _public_methods(NovaSonicToolAdapter) == {"result"}


def test_config_mapper_maps_inference_and_prompt_options():
    mapped = NovaSonicConfigMapper().map(
        "amazon.nova-sonic-v1:0",
        LiveConfigBase(
            provider_options={
                "inference": {"maxTokens": 64},
                "prompt_name": "proof",
            }
        ),
    )
    assert mapped[0]["event"]["sessionStart"]["inferenceConfiguration"] == {
        "maxTokens": 64
    }
    assert mapped[1]["event"]["promptStart"]["promptName"] == "proof"


def test_codec_encodes_inputs_and_decodes_events():
    codec = NovaSonicCodec()
    audio = codec.encode(AudioInput(payload=b"pcm"))
    text = codec.encode(TextInput(payload="hi"))
    events = codec.decode({"event": {"textOutput": {"content": "hello"}}})
    assert (
        audio["event"]["audioInput"]["content"]
        == base64.b64encode(b"pcm").decode()
    )
    assert text["event"]["textInput"]["content"] == "hi"
    assert events[0].payload == "hello"


def test_tool_adapter_builds_error_result():
    result = NovaSonicToolAdapter().result(
        "call-1", {"answer": 42}, is_error=True
    )
    assert result.call_id == "call-1"
    assert result.payload == {"answer": 42}
    assert result.is_error is True
