import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.agents.concrete import QAAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def groq_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqModel(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(groq_model):
    agent = QAAgent(llm=groq_model)
    assert agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type(groq_model):
    agent = QAAgent(llm=groq_model)
    assert agent.type == "QAAgent"


@pytest.mark.unit
def test_agent_exec(groq_model):
    agent = QAAgent(llm=groq_model)
    result = agent.exec("hello")
    assert type(result) == str


@pytest.mark.unit
def test_serialization(groq_model):
    agent = QAAgent(llm=groq_model)
    assert agent.id == QAAgent.model_validate_json(agent.model_dump_json()).id
