from abc import abstractmethod

from swarmauri_core.agents.IAgentCompaction import (
    CountInputTokens,
    IAgentCompaction,
)
from swarmauri_core.conversations.ICompactingConversation import (
    CompactionPlan,
    ICompactingConversation,
)

from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin


class AgentCompactionMixin(IAgentCompaction, AgentConversationMixin):
    """Orchestrate compaction with summarization supplied by the agent."""

    @abstractmethod
    def _summarize_compaction(self, plan: CompactionPlan) -> str:
        """Summarize the previous summary and eligible older messages."""

    @abstractmethod
    async def _asummarize_compaction(self, plan: CompactionPlan) -> str:
        """Asynchronously summarize the earlier conversation."""

    def compact(self, *, count_input_tokens: CountInputTokens) -> bool:
        conversation = self.conversation
        if not isinstance(conversation, ICompactingConversation):
            return False
        plan = conversation.plan_compaction()
        if plan is None:
            return False
        original_tokens = count_input_tokens(conversation.history)
        summary = self._summarize_compaction(plan)
        return self._apply_summary(
            conversation, plan, summary, original_tokens, count_input_tokens
        )

    async def acompact(self, *, count_input_tokens: CountInputTokens) -> bool:
        conversation = self.conversation
        if not isinstance(conversation, ICompactingConversation):
            return False
        plan = conversation.plan_compaction()
        if plan is None:
            return False
        original_tokens = count_input_tokens(conversation.history)
        summary = await self._asummarize_compaction(plan)
        return self._apply_summary(
            conversation, plan, summary, original_tokens, count_input_tokens
        )

    def compact_if_needed(
        self, *, count_input_tokens: CountInputTokens
    ) -> bool:
        return self._compaction_needed(count_input_tokens) and self.compact(
            count_input_tokens=count_input_tokens
        )

    async def acompact_if_needed(
        self, *, count_input_tokens: CountInputTokens
    ) -> bool:
        return self._compaction_needed(
            count_input_tokens
        ) and await self.acompact(count_input_tokens=count_input_tokens)

    def _compaction_needed(self, count_input_tokens: CountInputTokens) -> bool:
        conversation = self.conversation
        if not isinstance(conversation, ICompactingConversation):
            return False
        trigger = conversation.compaction_trigger_tokens
        return (
            trigger is not None
            and count_input_tokens(conversation.history) >= trigger
        )

    def _apply_summary(
        self,
        conversation: ICompactingConversation,
        plan: CompactionPlan,
        summary: str,
        original_tokens: int,
        count_input_tokens: CountInputTokens,
    ) -> bool:
        if self.conversation is not conversation or not summary.strip():
            return False
        proposed = conversation.preview_compaction(plan, summary)
        if count_input_tokens(proposed) >= original_tokens:
            return False
        return conversation.apply_compaction(plan, summary)
