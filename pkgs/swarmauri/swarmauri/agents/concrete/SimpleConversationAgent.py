from typing import Any, Optional, Dict, Literal, List, Union

from swarmauri.agents.base.AgentBase import AgentBase
from swarmauri.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.messages.concrete.HumanMessage import HumanMessage

from swarmauri_core.typing import SubclassUnion
from swarmauri.conversations.base.ConversationBase import ConversationBase

from swarmauri.messages.concrete.HumanMessage import contentItem


class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase]  #
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
