from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.messages.MessageBase import MessageBase

from .RealtimeTurn import RealtimeTurn


class SwarmauriConversationAdapter:
    def append_turn(
        self,
        conversation: ConversationBase | None,
        turn: RealtimeTurn,
    ) -> None:
        if conversation is None:
            return
        content = turn.output_text or turn.output_transcript
        if content:
            conversation.add_message(
                MessageBase(content=content, role="assistant")
            )
