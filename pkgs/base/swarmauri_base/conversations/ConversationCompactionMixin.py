from abc import abstractmethod
from collections.abc import Mapping, Sequence
from copy import deepcopy

from pydantic import Field
from swarmauri_core.conversations.ICompactingConversation import (
    CompactionPlan,
    ICompactingConversation,
)
from swarmauri_core.messages.IMessage import IMessage

from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.messages.MessageBase import MessageBase


class ConversationCompactionMixin(ICompactingConversation, ConversationBase):
    """Plan and apply compaction independently of any model."""

    summary: str | None = None
    trigger_tokens: int | None = Field(default=None, gt=0)
    keep_recent_turns: int = Field(default=4, ge=1)

    @property
    def compaction_trigger_tokens(self) -> int | None:
        return self.trigger_tokens

    @abstractmethod
    def _summary_message(self, summary: str) -> MessageBase:
        """Render summary text as historical context."""

    @staticmethod
    def _instruction_end(messages: Sequence[MessageBase]) -> int:
        for index, message in enumerate(messages):
            if message.role not in {"system", "developer"}:
                return index
        return len(messages)

    @property
    def history(self) -> list[MessageBase]:
        if not self.summary:
            return list(self.messages)
        start = self._instruction_end(self.messages)
        return [
            *self.messages[:start],
            self._summary_message(self.summary),
            *self.messages[start:],
        ]

    @staticmethod
    def _is_complete_turn(messages: Sequence[MessageBase]) -> bool:
        """Require a final reply and a result for every tool call."""
        pending: set[str] = set()
        answered = False
        for message in messages[1:]:
            if message.role == "assistant" and not pending:
                for call in getattr(message, "tool_calls", None) or ():
                    call_id = (
                        call.get("id")
                        if isinstance(call, Mapping)
                        else getattr(call, "id", None)
                    )
                    if (
                        not isinstance(call_id, str)
                        or not call_id
                        or call_id in pending
                    ):
                        return False
                    pending.add(call_id)
                answered = not pending
            elif message.role == "tool":
                call_id = getattr(message, "tool_call_id", None)
                if call_id not in pending:
                    return False
                pending.remove(call_id)
            else:
                return False
        return answered and not pending

    def plan_compaction(self) -> CompactionPlan | None:
        start = self._instruction_end(self.messages)
        turns = [
            index
            for index in range(start, len(self.messages))
            if self.messages[index].role == "user"
        ]
        if not turns or turns[0] != start:
            return None

        stop = start
        for begin, end in zip(turns[: -self.keep_recent_turns], turns[1:]):
            if not self._is_complete_turn(self.messages[begin:end]):
                break
            stop = end
        if stop == start:
            return None

        return CompactionPlan(
            messages=tuple(deepcopy(self.messages)),
            previous_summary=self.summary,
            start=start,
            stop=stop,
        )

    def preview_compaction(
        self, plan: CompactionPlan, summary: str
    ) -> list[IMessage]:
        return [
            *plan.messages[: plan.start],
            self._summary_message(summary.strip()),
            *plan.messages[plan.stop :],
        ]

    def apply_compaction(self, plan: CompactionPlan, summary: str) -> bool:
        summary = summary.strip()
        if not summary or self.plan_compaction() != plan:
            return False

        self.messages = (
            self.messages[: plan.start] + self.messages[plan.stop :]
        )
        self.summary = summary
        return True

    def clear_history(self) -> None:
        super().clear_history()
        self.summary = None
