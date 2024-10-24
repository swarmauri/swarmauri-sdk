import pytest
import os
from swarmauri.llms.concrete.GroqToolModel import GroqToolModel
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete import ToolAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def tool_agent():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")

    llm = GroqToolModel(api_key=API_KEY)
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    agent = ToolAgent(llm=llm, conversation=conversation, toolkit=toolkit)
    return agent


@pytest.mark.unit
def test_ubc_resource(tool_agent):
    assert tool_agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type(tool_agent):
    assert tool_agent.type == "ToolAgent"


@pytest.mark.unit
def test_serialization(tool_agent):
    assert (
        tool_agent.id == ToolAgent.model_validate_json(tool_agent.model_dump_json()).id
    )


@pytest.mark.unit
def test_agent_exec(tool_agent):
    result = tool_agent.exec("Add(512, 671)")
    assert type(result) is str
