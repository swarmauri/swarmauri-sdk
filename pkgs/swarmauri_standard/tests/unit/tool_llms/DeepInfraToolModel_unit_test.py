import logging
import os

import pytest
from dotenv import load_dotenv

from swarmauri_standard.agents.ToolAgent import ToolAgent
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.tool_llms.DeepInfraToolModel import DeepInfraToolModel as LLM
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_standard.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("DEEPINFRA_API_KEY")


@pytest.fixture(scope="module")
def deep_infra_tool_model():
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

    input_data = "what will the sum of 512 boys and 671 boys"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    return conversation


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(deep_infra_tool_model):
    assert deep_infra_tool_model.resource == "ToolLLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(deep_infra_tool_model):
    assert deep_infra_tool_model.type == "DeepInfraToolModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(deep_infra_tool_model):
    assert (
        deep_infra_tool_model.id
        == LLM.model_validate_json(deep_infra_tool_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(deep_infra_tool_model):
    assert deep_infra_tool_model.name == deep_infra_tool_model.allowed_models[0]


@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_agent_exec(deep_infra_tool_model, toolkit, conversation, model_name):
    deep_infra_tool_model.name = model_name

    agent = ToolAgent(
        llm=deep_infra_tool_model, conversation=conversation, toolkit=toolkit
    )
    result = agent.exec("Add 512+671")
    assert type(result) is str


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_predict(deep_infra_tool_model, toolkit, conversation, model_name):
    deep_infra_tool_model.name = model_name

    conversation = deep_infra_tool_model.predict(
        conversation=conversation, toolkit=toolkit
    )
    logging.info(conversation.get_last().content)
    assert type(conversation.get_last().content) is str


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_stream(deep_infra_tool_model, toolkit, conversation, model_name):
    deep_infra_tool_model.name = model_name

    collected_tokens = []
    for token in deep_infra_tool_model.stream(
        conversation=conversation, toolkit=toolkit
    ):
        logging.info(token)
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_batch(deep_infra_tool_model, toolkit, model_name):
    deep_infra_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = deep_infra_tool_model.batch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_apredict(deep_infra_tool_model, toolkit, conversation, model_name):
    deep_infra_tool_model.name = model_name

    result = await deep_infra_tool_model.apredict(
        conversation=conversation, toolkit=toolkit
    )
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_astream(deep_infra_tool_model, toolkit, conversation, model_name):
    deep_infra_tool_model.name = model_name

    collected_tokens = []
    async for token in deep_infra_tool_model.astream(
        conversation=conversation, toolkit=toolkit
    ):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    # assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_abatch(deep_infra_tool_model, toolkit, model_name):
    deep_infra_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await deep_infra_tool_model.abatch(
        conversations=conversations, toolkit=toolkit
    )
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
