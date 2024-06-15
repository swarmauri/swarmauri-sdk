import pytest
import os
from swarmauri.standard.llms.concrete.Groqmodel import Groqmodel
from swarmauri.standard.agents.concrete.ToolAgent import ToolAgent
from swarmauri.standard.conversations.concrete.Conversation import Conversation
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        conversation = Conversation()
        toolkit = Toolkit()
        tool = AdditionTool()
        toolkit.add_tool(tool)

        agent = ToolAgent(llm=llm, 
            conversation=conversation,
            tools=toolkit)
        assert agent.resource == 'Agent'
    test()

@pytest.mark.unit
def agent_exec_test():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        llm = GroqModel(api_key = API_KEY)
        conversation = Conversation()
        toolkit = Toolkit()
        tool = AdditionTool()
        toolkit.add_tool(tool)

        agent = ToolAgent(llm=llm, 
            conversation=conversation,
            tools=toolkit)
        result = agent.exec('Add 512+671')
        assert type(result) == str
    test()

