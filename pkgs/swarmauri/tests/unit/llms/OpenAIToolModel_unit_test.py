import pytest
import os
from swarmauri.llms.concrete.OpenAIToolModel import OpenAIToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.fixture(scope="module")
def openai_tool_model():
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(openai_tool_model):
    assert openai_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(openai_tool_model):
    assert openai_tool_model.type == "OpenAIToolModel"


@pytest.mark.unit
def test_serialization(openai_tool_model):
    assert (
        openai_tool_model.id
        == LLM.model_validate_json(openai_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(openai_tool_model):
    assert openai_tool_model.name == "gpt-3.5-turbo-0125"


@pytest.mark.unit
def test_agent_exec(openai_tool_model):
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    agent = ToolAgent(llm=openai_tool_model, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str
