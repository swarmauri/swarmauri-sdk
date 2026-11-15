from abc import abstractmethod
from dataclasses import dataclass

from swarmauri_core.conversations.IConversation import IConversation
from swarmauri_core.messages.IMessage import IMessage


@dataclass(frozen=True)
class CompactionPlan:
    """A snapshot of the messages and rolling summary at planning time."""

    messages: tuple[IMessage, ...]
    previous_summary: str | None
    start: int
    stop: int

    @property
    def older_messages(self) -> tuple[IMessage, ...]:
        return self.messages[self.start : self.stop]


class ICompactingConversation(IConversation):
    @property
    @abstractmethod
    def compaction_trigger_tokens(self) -> int | None:
        """Return the automatic threshold, if enabled."""
        pass

    @abstractmethod
    def plan_compaction(self) -> CompactionPlan | None:
        """Snapshot the older complete turns eligible for compaction."""
        pass

    @abstractmethod
    def preview_compaction(
        self, plan: CompactionPlan, summary: str
    ) -> list[IMessage]:
        """Render the proposed context without changing the conversation."""
        pass

    @abstractmethod
    def apply_compaction(self, plan: CompactionPlan, summary: str) -> bool:
        """Apply a nonempty summary if the conversation still matches the plan."""
        pass
