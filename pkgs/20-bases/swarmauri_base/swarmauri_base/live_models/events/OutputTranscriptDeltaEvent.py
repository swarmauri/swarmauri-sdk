from typing import Literal

from swarmauri_base.live_models.events.TextDeltaEvent import TextDeltaEvent


class OutputTranscriptDeltaEvent(TextDeltaEvent):
    kind: Literal["output_transcript_delta"] = "output_transcript_delta"
    type: Literal["OutputTranscriptDeltaEvent"] = "OutputTranscriptDeltaEvent"
