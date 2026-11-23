import base64
import json

from swarmauri_live_model_gemini import GeminiLiveCodec


def test_audio_and_transcript_are_both_emitted():
    message = json.dumps(
        {
            "serverContent": {
                "modelTurn": {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "audio/pcm",
                                "data": base64.b64encode(b"pcm").decode(),
                            }
                        }
                    ]
                },
                "outputTranscription": {"text": "hello"},
            }
        }
    )
    events = GeminiLiveCodec().decode(message)
    assert [event.kind for event in events] == [
        "audio_delta",
        "output_transcript_delta",
    ]
