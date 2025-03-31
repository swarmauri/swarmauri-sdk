from typing import Any, Optional, Union, Dict, Literal

from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.conversations.SessionCacheConversation import (
    SessionCacheConversation,
)

from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri_base.agents.AgentSystemContextMixin import AgentSystemContextMixin
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_core.messages import IMessage
from swarmauri_base.ComponentBase import SubclassUnion, ComponentBase


@ComponentBase.register_type(AgentBase, "RagAgent")
class RagAgent(
    AgentRetrieveMixin,
    AgentVectorStoreMixin,
    AgentSystemContextMixin,
    AgentConversationMixin,
    AgentBase,
):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    llm: SubclassUnion[LLMBase]
    conversation: Union[MaxSystemContextConversation, SessionCacheConversation] = (
        MaxSystemContextConversation(system_context="")
    )
    vector_store: SubclassUnion[VectorStoreBase]
    system_context: Union[SystemMessage, str] = SystemMessage(content="")
    type: Literal["RagAgent"] = "RagAgent"

    def _create_preamble_context(self):
        substr = self.system_context.content
        substr += "\n\n"
        substr += "\n".join([doc.content for doc in self.last_retrieved])
        return substr

    def _create_post_context(self):
        substr = "\n".join([doc.content for doc in self.last_retrieved])
        substr += "\n\n"
        substr += self.system_context.content
        return substr

    def _prepare_context(
        self,
        input_data: Union[str, IMessage],
        top_k: int,
        preamble: bool,
        fixed: bool,
    ) -> None:
        # Wrap input in a HumanMessage if it is a string
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of IMessage.")

        self.conversation.add_message(human_message)

        # Retrieval logic
        if top_k > 0 and len(self.vector_store.documents) > 0:
            self.last_retrieved = self.vector_store.retrieve(
                query=input_data, top_k=top_k
            )
            if preamble:
                new_context = self._create_preamble_context()
            else:
                new_context = self._create_post_context()
        else:
            if fixed:
                if preamble:
                    new_context = self._create_preamble_context()
                else:
                    new_context = self._create_post_context()
            else:
                new_context = self.system_context.content
                self.last_retrieved = []

        self.conversation.system_context = SystemMessage(content=new_context)

    def exec(
        self,
        input_data: Optional[Union[str, IMessage]] = "",
        top_k: int = 5,
        preamble: bool = True,
        fixed: bool = False,
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        llm_kwargs = llm_kwargs or self.llm_kwargs

        try:
            self._prepare_context(input_data, top_k, preamble, fixed)
            if llm_kwargs:
                self.llm.predict(conversation=self.conversation, **llm_kwargs)
            else:
                self.llm.predict(conversation=self.conversation)
            return self.conversation.get_last().content
        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e

    async def aexec(
        self,
        input_data: Optional[Union[str, IMessage]] = "",
        top_k: int = 5,
        preamble: bool = True,
        fixed: bool = False,
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        llm_kwargs = llm_kwargs or self.llm_kwargs

        try:
            self._prepare_context(input_data, top_k, preamble, fixed)
            if llm_kwargs:
                await self.llm.apredict(conversation=self.conversation, **llm_kwargs)
            else:
                await self.llm.apredict(conversation=self.conversation)
            return self.conversation.get_last().content
        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e
