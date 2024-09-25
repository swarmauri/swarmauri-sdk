import pytest
import os
from swarmauri_community.llms.concrete.ShuttleAIToolModel import (
    ShuttleAIToolModel as LLM,
)
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.fixture(scope="module")
def shuttleai_tool_model():
    API_KEY = os.getenv("SHUTTLEAI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(shuttleai_tool_model):
    assert shuttleai_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(shuttleai_tool_model):
    assert shuttleai_tool_model.type == "ShuttleAIToolModel"


@pytest.mark.unit
def test_serialization(shuttleai_tool_model):
    assert (
        shuttleai_tool_model.id
        == LLM.model_validate_json(shuttleai_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(shuttleai_tool_model):
    assert shuttleai_tool_model.name == "shuttle-2-turbo"


@pytest.mark.unit
def test_agent_exec(shuttleai_tool_model):
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    agent = ToolAgent(llm=llm, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str
