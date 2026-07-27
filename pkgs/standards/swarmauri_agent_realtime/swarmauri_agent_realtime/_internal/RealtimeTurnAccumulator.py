from swarmauri_base.live_models.events import (
    AudioDeltaEvent,
    InputTranscriptDeltaEvent,
    InterruptionEvent,
    OutputTranscriptDeltaEvent,
    TextDeltaEvent,
    ToolCallEvent,
    TurnCompleteEvent,
    UsageEvent,
)

from .RealtimeTurn import RealtimeTurn


class RealtimeTurnAccumulator:
    def __init__(self) -> None:
        self.turn = RealtimeTurn()

    def consume(self, event) -> RealtimeTurn:
        if isinstance(event, OutputTranscriptDeltaEvent):
            self.turn.output_transcript += str(event.payload or "")
        elif isinstance(event, InputTranscriptDeltaEvent):
            self.turn.input_transcript += str(event.payload or "")
        elif isinstance(event, TextDeltaEvent):
            self.turn.output_text += str(event.payload or "")
        elif isinstance(event, AudioDeltaEvent):
            self.turn.audio_chunks.append(event.payload)
        elif isinstance(event, ToolCallEvent):
            self.turn.tool_calls.append(event)
        elif isinstance(event, UsageEvent):
            self.turn.usage.update(event.payload)
        elif isinstance(event, InterruptionEvent):
            self.turn.interrupted = True
        elif isinstance(event, TurnCompleteEvent):
            self.turn.completed = True
        return self.turn
