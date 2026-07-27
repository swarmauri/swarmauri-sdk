from typing import Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class ImageInput(LiveInputBase):
    kind: Literal["image"] = "image"
    payload: bytes
    mime_type: str = "image/jpeg"
    type: Literal["ImageInput"] = "ImageInput"
