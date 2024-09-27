import pytest
import os
from swarmauri.llms.concrete.GeminiToolModel import GeminiToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.fixture(scope="module")
def gemini_tool_model():
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(gemini_tool_model):
    assert gemini_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(gemini_tool_model):
    assert gemini_tool_model.type == "GeminiToolModel"


@pytest.mark.unit
def test_serialization(gemini_tool_model):
    assert (
        gemini_tool_model.id
        == LLM.model_validate_json(gemini_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(gemini_tool_model):
    assert gemini_tool_model.name == "gemini-1.5-pro"


@pytest.mark.unit
def test_agent_exec(gemini_tool_model):
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    # Use geminitool_model from the fixture
    agent = ToolAgent(llm=gemini_tool_model, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str
