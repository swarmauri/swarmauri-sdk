import pytest
import os
from swarmauri.llms.concrete.MistralToolModel import MistralToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.fixture(scope="module")
def mistral_tool_model():
    API_KEY = os.getenv("MISTRAL_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(mistral_tool_model):
    assert mistral_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(mistral_tool_model):
    assert mistral_tool_model.type == "MistralToolModel"


@pytest.mark.unit
def test_serialization(mistral_tool_model):
    assert (
        mistral_tool_model.id
        == LLM.model_validate_json(mistral_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(mistral_tool_model):
    assert mistral_tool_model.name == "open-mixtral-8x22b"


@pytest.mark.unit
def test_agent_exec(mistral_tool_model):
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    # Use mistral_tool_model from the fixture
    agent = ToolAgent(
        llm=mistral_tool_model, conversation=conversation, toolkit=toolkit
    )
    result = agent.exec("Add 512+671")
    assert type(result) == str
