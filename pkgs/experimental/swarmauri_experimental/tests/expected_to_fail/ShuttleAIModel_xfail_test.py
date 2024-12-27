import pytest
import os
import asyncio
from swarmauri_experimental.llms.ShuttleAIModel import ShuttleAIModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from time import sleep
from dotenv import load_dotenv


def go_to_sleep():
    sleep(0.1)


load_dotenv()

API_KEY = os.getenv("SHUTTLEAI_API_KEY")


@pytest.fixture(scope="module")
def shuttleai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.unit
def test_no_system_context(shuttleai_model):
    go_to_sleep()

    model = shuttleai_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_nonpreamble_system_context(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
    model.name = model_name
    conversation = Conversation()

    # Say hi
    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    # Get Prediction
    model.predict(conversation=conversation)

    # Give System Context
    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    # Prompt
    input_data = "Hello Again."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert "Jeff" in prediction


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
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


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_multiple_system_contexts(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(conversation=conversation)

    system_context_2 = 'You only respond with the following phrase, "Ben"'
    human_message = SystemMessage(content=system_context_2)
    conversation.add_message(human_message)

    input_data_2 = "Hey"
    human_message = HumanMessage(content=input_data_2)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "Ben" in prediction


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
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


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
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


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
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
    assert len(full_response) > 0, "No tokens were received from the stream"
    assert conversation.get_last().content == full_response
    print(f"Received response: {full_response}")  # Add this line for debugging


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(shuttleai_model, model_name):
    go_to_sleep()

    model = shuttleai_model
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
    assert len(full_response) > 0, "No tokens were received from the stream"
    assert conversation.get_last().content == full_response
    print(f"Received response: {full_response}")  # Add this line for debugging
