import pytest
import os
from swarmauri.standard.llms.concrete.AnthropicToolModel import AnthropicToolModel
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent

@pytest.mark.unit
def test_ubc_resource():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        llm = AnthropicToolModel(api_key = API_KEY)
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
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        llm = AnthropicToolModel(api_key = API_KEY)
        assert llm.type == 'AnthropicModel'
    test()

@pytest.mark.unit
def test_default_name():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicToolModel(api_key = API_KEY)
        assert model.name == 'claude-3-haiku-20240307'
    test()

@pytest.mark.unit
def test_agent_exec():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        llm = AnthropicToolModel(api_key = API_KEY)
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

