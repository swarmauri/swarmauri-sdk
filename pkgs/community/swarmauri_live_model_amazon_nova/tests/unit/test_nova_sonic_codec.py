import base64

from swarmauri_live_model_amazon_nova import NovaSonicCodec


def test_audio_output():
    event = NovaSonicCodec().decode(
        {
            "event": {
                "audioOutput": {"content": base64.b64encode(b"pcm").decode()}
            }
        }
    )[0]
    assert event.payload == b"pcm"
