import logging
import os
import pytest
from swarmauri_standard.llms.AI21StudioModel import AI21StudioModel as LLM
from swarmauri_standard.conversations.Conversation import Conversation

from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage
from dotenv import load_dotenv

from swarmauri_standard.messages.AgentMessage import UsageData


load_dotenv()

API_KEY = os.getenv("AI21STUDIO_API_KEY")


@pytest.fixture(scope="module")
def ai21studio_model():
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
def test_ubc_resource(ai21studio_model):
    assert ai21studio_model.resource == "LLM"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_ubc_type(ai21studio_model):
    assert ai21studio_model.type == "AI21StudioModel"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_serialization(ai21studio_model):
    assert (
        ai21studio_model.id
        == LLM.model_validate_json(ai21studio_model.model_dump_json()).id
    )


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_default_name(ai21studio_model):
    assert ai21studio_model.name == ai21studio_model.allowed_models[0]


@pytest.mark.timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_no_system_context(ai21studio_model, model_name):
    model = ai21studio_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert isinstance(prediction, str)
    assert isinstance(conversation.get_last().usage, UsageData)
    logging.info(conversation.get_last().usage)


@pytest.mark.timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_preamble_system_context(ai21studio_model, model_name):
    model = ai21studio_model
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
    assert type(prediction) is str
    assert "Jeff" in prediction, f"Test failed for model: {model_name}"
    assert isinstance(conversation.get_last().usage, UsageData)


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(ai21studio_model, model_name):
    model = ai21studio_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Write a short story about a cat."
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


@pytest.mark.timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(ai21studio_model, model_name):
    model = ai21studio_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)
    assert isinstance(conversation.get_last().usage, UsageData)


@pytest.mark.timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(ai21studio_model, model_name):
    model = ai21studio_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Write a short story about a dog."
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


@pytest.mark.timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(ai21studio_model, model_name):
    model = ai21studio_model
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
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(ai21studio_model, model_name):
    model = ai21studio_model
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
