import pytest
import os
from swarmauri.standard.llms.concrete.GeminiToolModel import GeminiToolModel
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent

@pytest.mark.unit
def test_ubc_resource():
    def test():
        API_KEY = os.getenv('GEMINI_API_KEY')
        llm = GeminiToolModel(api_key = API_KEY)
        conversation = Conversation()
        toolkit = Toolkit()
        tool = AdditionTool()
        toolkit.add_tool(tool)

        agent = ToolAgent(llm=llm, 
            conversation=conversation,
            toolkit=toolkit)
        assert agent.resource == 'Agent'
    test()

@pytest.mark.unit
def test_ubc_type():
    def test():
        API_KEY = os.getenv('GEMINI_API_KEY')
        llm = GeminiToolModel(api_key = API_KEY)
        assert llm.type == 'GeminiToolModel'
    test()

@pytest.mark.unit
def test_default_name():
    def test():
        API_KEY = os.getenv('GEMINI_API_KEY')
        model = GeminiToolModel(api_key = API_KEY)
        assert model.name == ''
    test()

@pytest.mark.unit
def test_agent_exec():
    def test():
        API_KEY = os.getenv('GEMINI_API_KEY')
        llm = GeminiToolModel(api_key = API_KEY)
        conversation = Conversation()
        toolkit = Toolkit()
        tool = AdditionTool()
        toolkit.add_tool(tool)

        agent = ToolAgent(llm=llm, 
            conversation=conversation,
            toolkit=toolkit)
        result = agent.exec('Add 512+671')
        assert type(result) == str
    test()

