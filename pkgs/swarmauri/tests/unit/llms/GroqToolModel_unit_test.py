import pytest
import os
from swarmauri.llms.concrete.GroqToolModel import GroqToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.fixture(scope="module")
def groq_tool_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(groq_tool_model):
    assert groq_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(groq_tool_model):
    assert groq_tool_model.type == "GroqToolModel"


@pytest.mark.unit
def test_serialization(groq_tool_model):
    assert (
        groq_tool_model.id
        == LLM.model_validate_json(groq_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(groq_tool_model):
    assert groq_tool_model.name == "llama3-groq-70b-8192-tool-use-preview"


@pytest.mark.unit
def test_agent_exec(groq_tool_model):
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    # Use groq_tool_model from the fixture
    agent = ToolAgent(llm=groq_tool_model, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str
