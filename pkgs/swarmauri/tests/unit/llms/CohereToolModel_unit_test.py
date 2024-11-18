import logging

import pytest
import os
from swarmauri.llms.concrete.CohereToolModel import CohereToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent
from dotenv import load_dotenv

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("COHERE_API_KEY")


@pytest.fixture(scope="module")
def cohere_tool_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    return toolkit


@timeout(5)
@pytest.fixture(scope="module")
def conversation():
    conversation = Conversation()

    # Ensure the message has content that can be properly formatted
    input_data = {"type": "text", "text": "Add 512+671"}
    human_message = HumanMessage(content=[input_data])
    conversation.add_message(human_message)

    return conversation


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(cohere_tool_model):
    assert cohere_tool_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(cohere_tool_model):
    assert cohere_tool_model.type == "CohereToolModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(cohere_tool_model):
    assert (
        cohere_tool_model.id
        == LLM.model_validate_json(cohere_tool_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(cohere_tool_model):
    assert cohere_tool_model.name == "command-r"


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_agent_exec(cohere_tool_model, toolkit, conversation, model_name):
    cohere_tool_model.name = model_name

    agent = ToolAgent(llm=cohere_tool_model, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_predict(cohere_tool_model, toolkit, conversation, model_name):
    cohere_tool_model.name = model_name

    conversation = cohere_tool_model.predict(conversation=conversation, toolkit=toolkit)
    logging.info(conversation.get_last().content)

    assert type(conversation.get_last().content) == str


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_stream(cohere_tool_model, toolkit, conversation, model_name):
    cohere_tool_model.name = model_name

    collected_tokens = []
    for token in cohere_tool_model.stream(conversation=conversation, toolkit=toolkit):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_batch(cohere_tool_model, toolkit, model_name):
    cohere_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=[{"type": "text", "text": prompt}]))
        conversations.append(conv)

    results = cohere_tool_model.batch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_apredict(cohere_tool_model, toolkit, conversation, model_name):
    cohere_tool_model.name = model_name

    result = await cohere_tool_model.apredict(
        conversation=conversation, toolkit=toolkit
    )
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_astream(cohere_tool_model, toolkit, conversation, model_name):
    cohere_tool_model.name = model_name

    collected_tokens = []
    async for token in cohere_tool_model.astream(
        conversation=conversation, toolkit=toolkit
    ):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_abatch(cohere_tool_model, toolkit, model_name):
    cohere_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await cohere_tool_model.abatch(
        conversations=conversations, toolkit=toolkit
    )
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
