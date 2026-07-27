from typing import Literal

from pydantic import Field

from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class AudioDeltaEvent(LiveEventBase):
    kind: Literal["audio_delta"] = "audio_delta"
    payload: bytes
    mime_type: str = "audio/pcm"
    sample_rate: int = Field(default=24000, gt=0)
    channels: int = Field(default=1, gt=0)
    type: Literal["AudioDeltaEvent"] = "AudioDeltaEvent"
