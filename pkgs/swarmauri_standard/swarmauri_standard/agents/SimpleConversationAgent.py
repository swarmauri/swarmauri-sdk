from typing import Any, Dict, List, Literal, Optional

from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.llms.LLMBase import LLMBase

from swarmauri_standard.messages.HumanMessage import HumanMessage, contentItem


@ComponentBase.register_type(AgentBase, "SimpleConversationAgent")
class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    type: Literal["SimpleConversationAgent"] = "SimpleConversationAgent"

    def exec(
        self,
        input_data: Optional[str | List[contentItem]] = "",
        llm_kwargs: Optional[Dict] = None,
    ) -> Any:
        if llm_kwargs is None:
            llm_kwargs = {}
        if input_data:
            human_message = HumanMessage(content=input_data)
            self.conversation.add_message(human_message)

        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content

    async def aexec(
        self,
        input_data: Optional[str | List[contentItem]] = "",
        llm_kwargs: Optional[Dict] = None,
    ) -> Any:
        if llm_kwargs is None:
            llm_kwargs = {}
        if input_data:
            human_message = HumanMessage(content=input_data)
            self.conversation.add_message(human_message)

        await self.llm.apredict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content
