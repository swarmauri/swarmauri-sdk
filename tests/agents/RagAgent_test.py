import pytest
import os
from swarmauri.standard.llms.concrete.GroqModel import GroqModel
from swarmauri.standard.agents.concrete.RagAgent import RagAgent
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.standard.documents.concrete.Document import Document

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        conversation = Conversation()
        system_context = SystemMessage(content='Your name is Jeff.')
        vector_store = TfidfVectorStore()
        documents = [Document(content="Their sister's name is Jane."),
             Document(content="Their mother's name is Jean."),
             Document(content="Their father's name is Joseph."),
             Document(content="Their grandather's name is Alex.")]
        vector_store.add_documents(documents)


        agent = RagAgent(llm=llm, 
            conversation=conversation,
            system_context=system_context,
            vector_store=vector_store
            )
        assert agent.resource == 'Agent'
    test()

@pytest.mark.integration
def agent_exec_test():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        conversation = Conversation()
        system_context = SystemMessage(content='Your name is Jeff.')
        vector_store = TfidfVectorStore()
        documents = [Document(content="Their sister's name is Jane."),
             Document(content="Their mother's name is Jean."),
             Document(content="Their father's name is Joseph."),
             Document(content="Their grandather's name is Alex.")]
        vector_store.add_documents(documents)


        agent = RagAgent(llm=llm, 
            conversation=conversation,
            system_context=system_context,
            vector_store=vector_store
            )
        result = agent.exec("What is the name of their grandfather?")
        assert type(result) == str
    test()

