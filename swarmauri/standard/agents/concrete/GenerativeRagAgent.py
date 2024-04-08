from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.DocumentAgentBase import DocumentAgentBase
from swarmauri.standard.document_stores.base.DocumentStoreRetrieveBase import DocumentStoreRetrieveBase
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.chunkers.concrete.MdSnippetChunker import MdSnippetChunker
from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class GenerativeRagAgent(DocumentAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, document_store: DocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, document_store=document_store)

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
        
        
        
        similar_documents = self.document_store.retrieve(query=input_data, top_k=top_k)
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
        
        chunker = MdSnippetChunker()
        
        new_documents = [Document(doc_id=self.document_store.document_count()+1,
                                     content=each[2], 
                                     metadata={"source": "RagSaverAgent", 
                                               "language": each[1],
                                               "comments": each[0]})
                     for each in chunker.chunk_text(prediction)]

        self.document_store.add_documents(new_documents)
        
        return prediction
    
    
    
