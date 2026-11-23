from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase


class NovaSonicConfigMapper:
    def map(self, model: str, config: LiveConfigBase) -> list[dict]:
        return [
            {
                "event": {
                    "sessionStart": {
                        "inferenceConfiguration": config.provider_options.get(
                            "inference", {}
                        )
                    }
                }
            },
            {
                "event": {
                    "promptStart": {
                        "promptName": config.provider_options.get(
                            "prompt_name", "swarmauri"
                        ),
                        "textOutputConfiguration": {"mediaType": "text/plain"},
                        "audioOutputConfiguration": config.provider_options.get(  # noqa: E501
                            "audio_output",
                            {
                                "mediaType": "audio/lpcm",
                                "sampleRateHertz": 24000,
                                "sampleSizeBits": 16,
                                "channelCount": 1,
                                "voiceId": "matthew",
                                "encoding": "base64",
                                "audioType": "SPEECH",
                            },
                        ),
                    }
                }
            },
        ]
