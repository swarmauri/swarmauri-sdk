import pytest
import os
from swarmauri.standard.llms.concrete.MistralToolModel import MistralToolModel
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent

@pytest.mark.unit
def test_ubc_resource():
    def test():
        API_KEY = os.getenv('MISTRAL_API_KEY')
        llm = MistralToolModel(api_key = API_KEY)
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
        API_KEY = os.getenv('MISTRAL_API_KEY')
        llm = MistralToolModel(api_key = API_KEY)
        assert llm.type == 'MistralToolModel'
    test()

@pytest.mark.unit
def test_default_name():
    def test():
        API_KEY = os.getenv('MISTRAL_API_KEY')
        model = MistralToolModel(api_key = API_KEY)
        assert model.name == 'open-mixtral-8x22b'
    test()

@pytest.mark.unit
def test_agent_exec():
    def test():
        API_KEY = os.getenv('MISTRAL_API_KEY')
        llm = MistralToolModel(api_key = API_KEY)
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

