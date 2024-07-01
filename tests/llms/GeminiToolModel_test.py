import pytest
import os
from swarmauri.standard.llms.concrete.GeminiToolModel import GeminiToolModel as LLM
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent

@pytest.mark.unit
def test_ubc_resource():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.resource == 'LLM'

@pytest.mark.unit
def test_ubc_type():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.type == 'GeminiToolModel'

@pytest.mark.unit
def test_serialization():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.id == LLM.model_validate_json(llm.json()).id

@pytest.mark.unit
def test_default_name():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    assert model.name == 'gemini-1.5-pro-latest'

@pytest.mark.unit
def test_agent_exec():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    conversation = Conversation()
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    agent = ToolAgent(llm=llm, 
        conversation=conversation,
        toolkit=toolkit)
    result = agent.exec('Add 512+671')
    assert type(result) == str

