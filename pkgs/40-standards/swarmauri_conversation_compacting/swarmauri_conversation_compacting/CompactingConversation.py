from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.conversations.ConversationCompactionMixin import (
    ConversationCompactionMixin,
)
from swarmauri_standard.messages.AgentMessage import AgentMessage


@ComponentBase.register_type(ConversationBase, "CompactingConversation")
class CompactingConversation(ConversationCompactionMixin):
    """Expose a rolling summary and the retained conversation messages."""

    type: Literal["CompactingConversation"] = "CompactingConversation"

    def _summary_message(self, summary: str) -> AgentMessage:
        return AgentMessage(
            content=f"Summary of earlier conversation:\n{summary}"
        )
