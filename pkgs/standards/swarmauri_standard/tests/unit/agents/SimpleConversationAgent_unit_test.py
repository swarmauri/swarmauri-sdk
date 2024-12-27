import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.agents.concrete import SimpleConversationAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def simple_conversation_agent():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")

    llm = GroqModel(api_key=API_KEY)
    conversation = Conversation()
    agent = SimpleConversationAgent(conversation=conversation, llm=llm)
    return agent


@pytest.mark.unit
def test_ubc_resource(simple_conversation_agent):
    assert simple_conversation_agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type(simple_conversation_agent):
    assert simple_conversation_agent.type == "SimpleConversationAgent"


@pytest.mark.unit
def test_serialization(simple_conversation_agent):
    assert (
        simple_conversation_agent.id
        == SimpleConversationAgent.model_validate_json(
            simple_conversation_agent.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_agent_exec(simple_conversation_agent):
    result = simple_conversation_agent.exec("hello")
    assert type(result) == str
