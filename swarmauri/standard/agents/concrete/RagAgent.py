from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel

from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentRetrieveBase import AgentRetrieveBase
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.agents.base.VectorStoreAgentBase import VectorStoreAgentBase
from swarmauri.standard.agents.base.SystemContextAgentBase import SystemContextAgentBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)


class RagAgent(AgentBase, 
    AgentRetrieveBase,
    ConversationAgentBase, 
    NamedAgentBase, 
    SystemContextAgentBase, 
    VectorStoreAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, 
            system_context: Union[SystemMessage, str], 
            model: IModel, 
            conversation: SystemContextBase, 
            vector_store: VectorDocumentStoreRetrieveBase):
        AgentBase.__init__(self, model=model)
        AgentRetrieveBase.__init__(self)
        ConversationAgentBase.__init__(self, conversation=conversation)
        NamedAgentBase.__init__(self, name=name)
        SystemContextAgentBase.__init__(self, system_context=system_context)
        VectorStoreAgentBase.__init__(self, vector_store=vector_store)

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
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             preamble: bool = True,
             fixed: bool = False,
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
        try:
            conversation = self.conversation
            model = self.model

            # Check if the input is a string, then wrap it in a HumanMessage
            if isinstance(input_data, str):
                human_message = HumanMessage(input_data)
            elif isinstance(input_data, IMessage):
                human_message = input_data
            else:
                raise TypeError("Input data must be a string or an instance of Message.")
            
            # Add the human message to the conversation
            conversation.add_message(human_message)

            # Retrieval and set new substr for system context
            if top_k > 0:
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
            system_context = SystemMessage(substr)
            conversation.system_context = system_context
            

            # Retrieve the conversation history and predict a response
            messages = conversation.as_messages()
            if model_kwargs:
                prediction = model.predict(messages=messages, **model_kwargs)
            else:
                prediction = model.predict(messages=messages)
                
            # Create an AgentMessage instance with the model's response and update the conversation
            agent_message = AgentMessage(prediction)
            conversation.add_message(agent_message)
            
            return prediction
        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e
