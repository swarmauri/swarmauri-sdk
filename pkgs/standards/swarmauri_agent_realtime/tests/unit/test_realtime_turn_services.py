from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.live_models.events import (
    AudioDeltaEvent,
    OutputTranscriptDeltaEvent,
    TextDeltaEvent,
    TurnCompleteEvent,
    UsageEvent,
)
from swarmauri_agent_realtime._internal.RealtimeTurnAccumulator import (
    RealtimeTurnAccumulator,
)
from swarmauri_agent_realtime._internal.SwarmauriConversationAdapter import (
    SwarmauriConversationAdapter,
)


def test_accumulator_preserves_independent_modalities_and_usage() -> None:
    accumulator = RealtimeTurnAccumulator()
    accumulator.consume(TextDeltaEvent(payload="visible"))
    accumulator.consume(OutputTranscriptDeltaEvent(payload="spoken"))
    accumulator.consume(AudioDeltaEvent(payload=b"audio"))
    accumulator.consume(UsageEvent(payload={"output_tokens": 3}))
    turn = accumulator.consume(TurnCompleteEvent())

    assert turn.output_text == "visible"
    assert turn.output_transcript == "spoken"
    assert turn.audio_chunks == [b"audio"]
    assert turn.usage == {"output_tokens": 3}
    assert turn.completed


def test_conversation_adapter_prefers_explicit_text() -> None:
    accumulator = RealtimeTurnAccumulator()
    accumulator.consume(TextDeltaEvent(payload="text"))
    accumulator.consume(OutputTranscriptDeltaEvent(payload="transcript"))
    conversation = ConversationBase()

    SwarmauriConversationAdapter().append_turn(conversation, accumulator.turn)

    assert conversation.get_last().content == "text"
