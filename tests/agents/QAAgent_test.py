import pytest
import os
from swarmauri.standard.llms.concrete.GroqModel import GroqModel
from swarmauri.standard.agents.concrete.QAAgent import QAAgent


@pytest.mark.unit
def test_ubc_resource():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        agent = QAAgent(llm=llm)
        assert agent.resource == 'Agent'
    test()

@pytest.mark.unit
def test_agent_exec():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        
        agent = QAAgent(llm=llm)
        result = agent.exec('hello')
        assert type(result) == str
    test()

