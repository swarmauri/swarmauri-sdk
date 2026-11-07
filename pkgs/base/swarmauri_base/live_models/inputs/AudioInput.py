from typing import Literal

from pydantic import Field

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class AudioInput(LiveInputBase):
    kind: Literal["audio"] = "audio"
    payload: bytes
    mime_type: str = "audio/pcm"
    sample_rate: int = Field(default=16000, gt=0)
    channels: int = Field(default=1, gt=0)
    type: Literal["AudioInput"] = "AudioInput"
