"""Native DeepInfra synthesis, isolated from OpenAI speech."""

from typing import Any, ClassVar, Literal
import httpx
from pydantic import Field, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tts.JsonAudioTTSMixin import JsonAudioTTSMixin
from swarmauri_base.tts.TTSBase import TTSBase


@ComponentBase.register_type(TTSBase, "DeepInfraKokoroTTS")
class DeepInfraKokoroTTS(JsonAudioTTSMixin, TTSBase):
    """Decode native JSON audio; streaming is intentionally unsupported."""

    _speech_url: ClassVar[str] = (
        "https://api.deepinfra.com/v1/inference/hexgrad/Kokoro-82M"
    )
    api_key: SecretStr = Field(repr=False, min_length=1)
    timeout: float = Field(default=120, gt=0)
    allowed_models: list[str] = ["hexgrad/Kokoro-82M"]
    name: str = Field(default="hexgrad/Kokoro-82M", min_length=1)
    type: Literal["DeepInfraKokoroTTS"] = "DeepInfraKokoroTTS"
    response_format: Literal["mp3", "opus", "flac", "wav", "pcm"] = "wav"
    allowed_voices: ClassVar[frozenset[str]] = frozenset(
        [
            "af_alloy",
            "af_aoede",
            "af_bella",
            "af_heart",
            "af_jessica",
            "af_kore",
            "af_nicole",
            "af_nova",
            "af_river",
            "af_sarah",
            "af_sky",
            "am_adam",
            "am_echo",
            "am_eric",
            "am_fenrir",
            "am_liam",
            "am_michael",
            "am_onyx",
            "am_puck",
            "am_santa",
            "bf_alice",
            "bf_emma",
            "bf_isabella",
            "bf_lily",
            "bm_daniel",
            "bm_fable",
            "bm_george",
            "bm_lewis",
            "ef_dora",
            "em_alex",
            "em_santa",
            "ff_siwis",
            "hf_alpha",
            "hf_beta",
            "hm_omega",
            "hm_psi",
            "if_sara",
            "im_nicola",
            "jf_alpha",
            "jf_gongitsune",
            "jf_nezumi",
            "jf_tebukuro",
            "jm_kumo",
            "pf_dora",
            "pm_alex",
            "pm_santa",
            "zf_xiaobei",
            "zf_xiaoni",
            "zf_xiaoxiao",
            "zf_xiaoyi",
            "zm_yunjian",
            "zm_yunxi",
            "zm_yunxia",
            "zm_yunyang",
        ]
    )
    preset_voices: list[str] = Field(default=["af_bella"], min_length=1)
    speed: float = Field(default=1.0, ge=0.25, le=4)

    def _speech_payload(self, text: str, streaming: bool) -> dict[str, Any]:
        if len(text) > 10000:
            raise ValueError(
                "Input exceeds this native model's character limit."
            )
        if any(
            voice not in self.allowed_voices for voice in self.preset_voices
        ):
            raise ValueError("Unsupported Kokoro preset voice.")
        return {
            "text": text,
            "preset_voice": self.preset_voices,
            "output_format": self.response_format,
            "speed": self.speed,
            "stream": False,
        }

    def _audio_object(self, response: httpx.Response) -> dict[str, Any]:
        data = super()._audio_object(response)
        status = data.get("inference_status", {})
        if (
            not isinstance(status, dict)
            or status.get("status", "succeeded") != "succeeded"
        ):
            raise RuntimeError("Native speech inference did not succeed.")
        if data.get("output_format") not in (None, "", self.response_format):
            raise ValueError(
                "Native speech output format differs from the request."
            )
        return data
