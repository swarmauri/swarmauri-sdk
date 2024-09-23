import pytest
import os
from swarmauri.llms.concrete.OpenAIToolModel import OpenAIToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_ubc_resource():
    API_KEY = os.getenv("OPENAI_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.resource == "LLM"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_ubc_type():
    API_KEY = os.getenv("OPENAI_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.type == "OpenAIToolModel"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_serialization():
    API_KEY = os.getenv("OPENAI_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_default_name():
    API_KEY = os.getenv("OPENAI_API_KEY")
    model = LLM(api_key=API_KEY)
    assert model.name == "gpt-3.5-turbo-0125"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_agent_exec():
    API_KEY = os.getenv("OPENAI_API_KEY")
    llm = LLM(api_key=API_KEY)
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    agent = ToolAgent(llm=llm, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str
