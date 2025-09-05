# File: tests/llms/test_cerebras_model.py

import json
import logging
import os

import pytest
from dotenv import load_dotenv

from swarmauri_standard.llms.CerebrasModel import CerebrasModel as LLM
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.messages.AgentMessage import UsageData

load_dotenv()
API_KEY = os.getenv("CEREBRAS_API_KEY")


@pytest.fixture(scope="module")
def cerebras_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.timeout(5)
def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_resource(cerebras_model):
    assert cerebras_model.resource == "LLM"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_type(cerebras_model):
    assert cerebras_model.type == "CerebrasModel"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_serialization(cerebras_model):
    assert (
        cerebras_model.id
        == LLM.model_validate_json(cerebras_model.model_dump_json()).id
    )


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_default_name(cerebras_model):
    assert cerebras_model.name == cerebras_model.allowed_models[0]


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(cerebras_model, model_name):
    model = cerebras_model
    model.name = model_name
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Hello"))

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    logging.info(usage_data)

    assert isinstance(prediction, str)
    assert isinstance(usage_data, UsageData)


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(cerebras_model, model_name):
    model = cerebras_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    conversation.add_message(SystemMessage(content=system_context))
    conversation.add_message(HumanMessage(content=json.dumps("Hi")))

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    logging.info(usage_data)

    assert isinstance(prediction, str)
    assert isinstance(usage_data, UsageData)


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(cerebras_model, model_name):
    model = cerebras_model
    model.name = model_name
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Write a short story about a cat."))

    collected_tokens = []
    for token in model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(cerebras_model, model_name):
    model = cerebras_model
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


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_apredict(cerebras_model, model_name):
    model = cerebras_model
    model.name = model_name
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Hello"))

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_astream(cerebras_model, model_name):
    model = cerebras_model
    model.name = model_name
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Write a short story about a dog."))

    collected_tokens = []
    async for token in model.astream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(cerebras_model, model_name):
    model = cerebras_model
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
