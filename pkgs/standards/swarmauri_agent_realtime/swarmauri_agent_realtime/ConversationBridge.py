from typing import Any


class ConversationBridge:
    """Bridges completed live turns to existing conversation objects."""

    def initial_history(self, conversation: Any) -> list[Any]:
        if conversation is None:
            return []
        return list(
            getattr(
                conversation, "history", getattr(conversation, "messages", [])
            )
        )

    def append(self, conversation: Any, message: Any) -> None:
        if conversation is None:
            return
        if hasattr(conversation, "add_message"):
            conversation.add_message(message)
        elif hasattr(conversation, "history"):
            conversation.history.append(message)
        elif hasattr(conversation, "messages"):
            conversation.messages.append(message)
