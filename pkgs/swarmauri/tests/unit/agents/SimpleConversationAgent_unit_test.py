import logging
import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.agents.concrete.SimpleConversationAgent import SimpleConversationAgent

def test_ubc_resource():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    conversation=Conversation()
    agent = SimpleConversationAgent(conversation=conversation, 
                                    llm=llm)
    assert agent.resource == 'Agent'

@pytest.mark.unit
def test_ubc_type():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    conversation=Conversation()
    agent = SimpleConversationAgent(conversation=conversation, 
                                    llm=llm)
    assert agent.type == 'SimpleConversationAgent'

@pytest.mark.unit
def test_serialization():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    conversation=Conversation()
    agent = SimpleConversationAgent(conversation=conversation, 
                                        llm=llm)
    assert agent.id == SimpleConversationAgent.model_validate_json(agent.model_dump_json()).id

@pytest.mark.unit
def test_agent_exec():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    conversation=Conversation()
    agent = SimpleConversationAgent(conversation=conversation, 
                                    llm=llm)
    result = agent.exec('hello')
    assert type(result) == str
