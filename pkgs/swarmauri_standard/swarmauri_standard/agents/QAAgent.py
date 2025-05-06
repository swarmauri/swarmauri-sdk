from typing import Any, Optional, Dict, Literal

from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import SubclassUnion, ComponentBase


@ComponentBase.register_type(AgentBase, "QAAgent")
class QAAgent(AgentBase):
    conversation: SubclassUnion[ConversationBase] = MaxSystemContextConversation(
        max_size=2
    )
    type: Literal["QAAgent"] = "QAAgent"

    def exec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        llm_kwargs = llm_kwargs or self.llm_kwargs

        self.conversation.add_message(HumanMessage(content=input_str))
        self.llm.predict(conversation=self.conversation, **llm_kwargs)

        return self.conversation.get_last().content

    async def aexec(
        self, input_str: Optional[str] = "", llm_kwargs: Optional[Dict] = {}
    ) -> Any:
        llm_kwargs = llm_kwargs or self.llm_kwargs

        self.conversation.add_message(HumanMessage(content=input_str))
        await self.llm.apredict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content
