from typing import Literal

from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent


class InputTranscriptDeltaEvent(TextDeltaEvent):
    kind: Literal["input_transcript_delta"] = "input_transcript_delta"
    type: Literal["InputTranscriptDeltaEvent"] = "InputTranscriptDeltaEvent"
