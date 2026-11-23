from typing import Literal

from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class TextInput(LiveInputBase):
    kind: Literal["text"] = "text"
    payload: str
    mime_type: str = "text/plain"
    type: Literal["TextInput"] = "TextInput"
