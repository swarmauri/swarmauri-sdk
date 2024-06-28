import pytest
import os
from swarmauri.standard.llms.concrete.GroqToolModel import GroqToolModel
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent

@pytest.mark.unit
def test_ubc_resource():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqToolModel(api_key = API_KEY)
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
def test_agent_exec():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqToolModel(api_key = API_KEY)
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

