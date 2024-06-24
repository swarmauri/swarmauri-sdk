from typing import Any, Optional, Union, Dict, Literal
from swarmauri.core.messages import IMessage
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri.standard.agents.base.AgentSystemContextMixin import AgentSystemContextMixin

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class RagAgent(AgentRetrieveMixin, 
               AgentVectorStoreMixin, 
               AgentSystemContextMixin, 
               AgentConversationMixin, 
               AgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """
    
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
            conversation = self.conversation
            llm = self.llm

            # Check if the input is a string, then wrap it in a HumanMessage
            if isinstance(input_data, str):
                human_message = HumanMessage(content=input_data)
            elif isinstance(input_data, IMessage):
                human_message = input_data
            else:
                raise TypeError("Input data must be a string or an instance of Message.")
            
            # Add the human message to the conversation
            conversation.add_message(human_message)

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
            conversation.system_context = system_context
            

            # Retrieve the conversation history and predict a response
            messages = conversation.as_messages()
            if llm_kwargs:
                prediction = llm.predict(messages=messages, **llm_kwargs)
            else:
                prediction = llm.predict(messages=messages)
                
            # Create an AgentMessage instance with the model's response and update the conversation
            agent_message = AgentMessage(content=prediction)
            conversation.add_message(agent_message)
            
            return prediction
        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e