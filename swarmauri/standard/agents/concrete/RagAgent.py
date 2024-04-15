from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.VectorStoreAgentBase import VectorStoreAgentBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class RagAgent(VectorStoreAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, vector_store: VectorDocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, vector_store=vector_store)

    def exec(self, 
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
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
        
        
        
        similar_documents = self.vector_store.retrieve(query=input_data, top_k=top_k)
        substr = '\n'.join([doc.content for doc in similar_documents])
        
        # Use substr to set system context
        system_context = SystemMessage(substr)
        conversation.system_context = system_context
        

        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
            
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction
    
    
    
