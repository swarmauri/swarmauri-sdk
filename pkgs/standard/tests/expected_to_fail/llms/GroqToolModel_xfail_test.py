import logging

import pytest
import os
from swarmauri.llms.concrete.GroqToolModel import GroqToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

failing_llms = ["llama3-8b-8192"]


@pytest.fixture(scope="module")
def groq_tool_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    return toolkit


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", failing_llms)
async def test_abatch(groq_tool_model, toolkit, model_name):
    groq_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await groq_tool_model.abatch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
