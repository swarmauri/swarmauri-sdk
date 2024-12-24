from typing import Any, Optional, Dict, Literal, List, Union

from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.conversations.ConversationBase import ConversationBase

from swarmauri_standard.messages.HumanMessage import contentItem


class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase]  #
    type: Literal["SimpleConversationAgent"] = "SimpleConversationAgent"

    def exec(
        self,
        input_data: Optional[Union[str, List[contentItem]]] = "",
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:

        if input_str:
            human_message = HumanMessage(content=input_str)
            self.conversation.add_message(human_message)

        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content
