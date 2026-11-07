from typing import Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class VideoInput(LiveInputBase):
    kind: Literal["video"] = "video"
    payload: bytes
    mime_type: str = "video/mp4"
    type: Literal["VideoInput"] = "VideoInput"
