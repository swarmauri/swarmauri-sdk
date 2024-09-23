import pytest
import logging
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.agents.concrete.QAAgent import QAAgent

@pytest.mark.unit
def test_ubc_resource():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    agent = QAAgent(llm=llm)
    assert agent.resource == 'Agent'

@pytest.mark.unit
def test_ubc_type():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    agent = QAAgent(llm=llm)
    assert agent.type == 'QAAgent'

@pytest.mark.unit
def test_agent_exec():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    
    agent = QAAgent(llm=llm)
    result = agent.exec('hello')
    assert type(result) == str

@pytest.mark.unit
def test_serialization():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    
    agent = QAAgent(llm=llm)
    assert agent.id == QAAgent.model_validate_json(agent.model_dump_json()).id