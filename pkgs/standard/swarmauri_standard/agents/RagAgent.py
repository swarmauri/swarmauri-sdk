from typing import Any, Optional, Union, Dict, Literal
from swarmauri_core.messages import IMessage

from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri_base.agents.AgentSystemContextMixin import AgentSystemContextMixin

from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.messages.AgentMessage import AgentMessage

from swarmauri_core.typing import SubclassUnion
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase

class RagAgent(AgentRetrieveMixin, 
               AgentVectorStoreMixin, 
               AgentSystemContextMixin, 
               AgentConversationMixin, 
               AgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    vector_store: SubclassUnion[VectorStoreBase]
    system_context:  Union[SystemMessage, str]
    type: Literal['RagAgent'] = 'RagAgent'
    
    def _create_preamble_context(self):
        substr = self.system_context.content
        substr += '\n\n'
        substr += '\n'.join([doc.content for doc in self.last_retrieved])
        return substr

    def _create_post_context(self):
        substr = '\n'.join([doc.content for doc in self.last_retrieved])
        substr += '\n\n'
        substr += self.system_context.content
        return substr

    def exec(self, 
             input_data: Optional[Union[str, IMessage]] = "", 
             top_k: int = 5, 
             preamble: bool = True,
             fixed: bool = False,
             llm_kwargs: Optional[Dict] = {}
             ) -> Any:
        try:
            # Check if the input is a string, then wrap it in a HumanMessage
            if isinstance(input_data, str):
                human_message = HumanMessage(content=input_data)
            elif isinstance(input_data, IMessage):
                human_message = input_data
            else:
                raise TypeError("Input data must be a string or an instance of Message.")
            
            # Add the human message to the conversation
            self.conversation.add_message(human_message)

            # Retrieval and set new substr for system context
            if top_k > 0 and len(self.vector_store.documents) > 0:
                self.last_retrieved = self.vector_store.retrieve(query=input_data, top_k=top_k)

                if preamble:
                    substr = self._create_preamble_context()
                else:
                    substr = self._create_post_context()

            else:
                if fixed:
                    if preamble:
                        substr = self._create_preamble_context()
                    else:
                        substr = self._create_post_context()
                else:
                    substr = self.system_context.content
                    self.last_retrieved = []
                
            # Use substr to set system context
            system_context = SystemMessage(content=substr)
            self.conversation.system_context = system_context
            

            # Retrieve the conversation history and predict a response
            if llm_kwargs:
                self.llm.predict(conversation=self.conversation, **llm_kwargs)
            else:
                self.llm.predict(conversation=self.conversation)
                
            return self.conversation.get_last().content

        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e