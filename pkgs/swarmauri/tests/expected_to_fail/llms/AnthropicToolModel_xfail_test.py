import logging
import pytest
import os
from swarmauri.llms.concrete.AnthropicToolModel import AnthropicToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout


load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def anthropic_tool_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)
    return toolkit


@pytest.fixture(scope="module")
def conversation():
    conversation = Conversation()
    input_data = "Add 50 and 50"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)
    return conversation


@timeout(5)
@pytest.mark.xfail(reason="This test is expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_stream(anthropic_tool_model, toolkit, conversation, model_name):
    anthropic_tool_model.name = model_name
    collected_tokens = []
    for token in anthropic_tool_model.stream(
        conversation=conversation, toolkit=toolkit
    ):
        logging.info(token)
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.xfail(reason="This test is expected to fail")
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_astream(anthropic_tool_model, toolkit, conversation, model_name):
    anthropic_tool_model.name = model_name
    collected_tokens = []
    async for token in anthropic_tool_model.astream(
        conversation=conversation, toolkit=toolkit
    ):
        assert isinstance(token, str)
        # logging.info(token)
        collected_tokens.append(token)
    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response
