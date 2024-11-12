import logging

import pytest
import os
from swarmauri.llms.concrete.AnthropicModel import AnthropicModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.timeout_wrapper import timeout
from swarmauri.utils.retry_decorator import retry_on_status_codes

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def anthropic_model():
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
@pytest.mark.unit
def test_ubc_resource(anthropic_model):
    assert anthropic_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(anthropic_model):
    assert anthropic_model.type == "AnthropicModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(anthropic_model):
    assert (
        anthropic_model.id
        == LLM.model_validate_json(anthropic_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(anthropic_model):
    assert anthropic_model.name == "claude-3-haiku-20240307"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name

    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert isinstance(conversation.get_last().usage, UsageData)
    logging.info(conversation.get_last().usage)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "Jeff" in prediction
    assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name
    conversation = Conversation()

    input_data = "How how do you do?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response
    assert isinstance(conversation.get_last().usage, UsageData)
    logging.info(conversation.get_last().usage)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name

    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = model.batch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
        assert isinstance(result.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
@retry_on_status_codes([429, 529])
async def test_apredict(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)
    assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_astream(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name
    conversation = Conversation()

    input_data = "How how do you do?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    async for token in model.astream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response
    assert isinstance(conversation.get_last().usage, UsageData)
    logging.info(conversation.get_last().usage)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(anthropic_model, model_name):
    model = anthropic_model
    model.name = model_name

    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await model.abatch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
        assert isinstance(result.get_last().usage, UsageData)
