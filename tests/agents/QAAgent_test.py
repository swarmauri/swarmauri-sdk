import pytest
import logging
import os
from swarmauri.standard.llms.concrete.GroqModel import GroqModel
from swarmauri.standard.agents.concrete.QAAgent import QAAgent
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.llms.base.LLMBase import LLMBase

@pytest.mark.unit
def test_ubc_resource():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    logging.info(str(SubclassUnion[LLMBase]))
    agent = QAAgent(llm=llm)
    assert agent.resource == 'Agent'


@pytest.mark.unit
def test_agent_exec():
    API_KEY = os.getenv('GROQ_API_KEY')
    llm = GroqModel(api_key = API_KEY)
    
    agent = QAAgent(llm=llm)
    result = agent.exec('hello')
    assert type(result) == str


