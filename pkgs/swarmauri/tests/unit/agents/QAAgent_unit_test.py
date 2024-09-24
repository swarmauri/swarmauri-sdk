import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.agents.concrete.QAAgent import QAAgent
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")


@pytest.mark.unit
def test_ubc_resource():
    llm = GroqModel(api_key=API_KEY)
    agent = QAAgent(llm=llm)
    assert agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type():
    llm = GroqModel(api_key=API_KEY)
    agent = QAAgent(llm=llm)
    assert agent.type == "QAAgent"


@pytest.mark.unit
def test_agent_exec():
    llm = GroqModel(api_key=API_KEY)

    agent = QAAgent(llm=llm)
    result = agent.exec("hello")
    assert type(result) == str


@pytest.mark.unit
def test_serialization():
    llm = GroqModel(api_key=API_KEY)

    agent = QAAgent(llm=llm)
    assert agent.id == QAAgent.model_validate_json(agent.model_dump_json()).id
