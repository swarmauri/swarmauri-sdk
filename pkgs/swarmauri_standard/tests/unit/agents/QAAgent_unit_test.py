import pytest
import os
from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.agents.QAAgent import QAAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def qa_agent():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqModel(api_key=API_KEY)
    agent = QAAgent(llm=llm)
    return agent


@pytest.mark.unit
def test_ubc_resource(qa_agent):
    assert qa_agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type(qa_agent):
    assert qa_agent.type == "QAAgent"


@pytest.mark.unit
def test_agent_exec(qa_agent):
    result = qa_agent.exec("hello")
    assert isinstance(result, str)


@pytest.mark.unit
def test_serialization(qa_agent):
    assert qa_agent.id == QAAgent.model_validate_json(qa_agent.model_dump_json()).id


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_aexec(qa_agent):
    result = await qa_agent.aexec("hello")
    assert isinstance(result, str)
