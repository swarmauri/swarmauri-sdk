from typing import Any, Optional, Dict, Literal, List, Union

from swarmauri_standard.messages.HumanMessage import contentItem
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import SubclassUnion, ComponentBase


@ComponentBase.register_type(AgentBase, "SimpleConversationAgent")
class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    type: Literal["SimpleConversationAgent"] = "SimpleConversationAgent"

    def exec(
        self,
        input_data: Optional[Union[str, List[contentItem]]] = "",
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        if input_data:
            human_message = HumanMessage(content=input_data)
            self.conversation.add_message(human_message)

        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content

    async def aexec(
        self,
        input_data: Optional[Union[str, List[contentItem]]] = "",
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        if input_data:
            human_message = HumanMessage(content=input_data)
            self.conversation.add_message(human_message)

        await self.llm.apredict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content
