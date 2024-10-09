import pytest
import os
import asyncio
from swarmauri.llms.concrete.LeptonAIModel import LeptonAIModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage

API_KEY = os.getenv("LEPTON_API_KEY")


@pytest.fixture(scope="module")
def leptonai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(leptonai_model):
    assert leptonai_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(leptonai_model):
    assert leptonai_model.type == "LeptonAIModel"


@pytest.mark.unit
def test_serialization(leptonai_model):
    assert (
        leptonai_model.id
        == LLM.model_validate_json(leptonai_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(leptonai_model):
    assert leptonai_model.name == "llama3-8b"


@pytest.mark.unit
def test_no_system_context(leptonai_model):
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    leptonai_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.unit
def test_preamble_system_context(leptonai_model):
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    leptonai_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert isinstance(prediction, str)
    assert "Jeff" in prediction


@pytest.mark.acceptance
def test_nonpreamble_system_context(leptonai_model):
    conversation = Conversation()

    # Say hi
    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    # Get Prediction
    leptonai_model.predict(conversation=conversation)

    # Give System Context
    system_context = 'You only respond with the following phrase, "Jeff"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    # Prompt
    input_data = "Hello Again."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    leptonai_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert "Jeff" in prediction


@pytest.mark.acceptance
def test_multiple_system_contexts(leptonai_model):
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    leptonai_model.predict(conversation=conversation)

    system_context_2 = 'You only respond with the following phrase, "Ben"'
    system_message = SystemMessage(content=system_context_2)
    conversation.add_message(system_message)

    input_data_2 = "Hey"
    human_message = HumanMessage(content=input_data_2)
    conversation.add_message(human_message)

    leptonai_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert isinstance(prediction, str)
    assert "Ben" in prediction


# Tests for streaming
@pytest.mark.unit
def test_stream(leptonai_model):
    conversation = Conversation()

    input_data = "Write a short story about a cat."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in leptonai_model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.unit
def test_stream_with_system_context(leptonai_model):
    conversation = Conversation()

    system_context = "You are a helpful assistant who likes cats."
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Tell me about cats."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in leptonai_model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


# Tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_apredict(leptonai_model):
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await leptonai_model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_apredict_with_system_context(leptonai_model):
    conversation = Conversation()

    system_context = "You are a helpful assistant who likes dogs."
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Tell me about dogs."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await leptonai_model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_astream(leptonai_model):
    conversation = Conversation()

    input_data = "Write a short story about a dog."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    async for token in leptonai_model.astream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


# Tests for batch operations
@pytest.mark.unit
def test_batch(leptonai_model):
    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = leptonai_model.batch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(leptonai_model):
    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await leptonai_model.abatch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


# Test batch operations with system context
@pytest.mark.unit
def test_batch_with_system_context(leptonai_model):
    conversations = []
    system_context = "You are a helpful assistant."

    for prompt in ["Tell me about cats", "Tell me about dogs", "Tell me about birds"]:
        conv = Conversation()
        conv.add_message(SystemMessage(content=system_context))
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = leptonai_model.batch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch_with_system_context(leptonai_model):
    conversations = []
    system_context = "You are a helpful assistant."

    for prompt in [
        "Tell me about planets",
        "Tell me about stars",
        "Tell me about galaxies",
    ]:
        conv = Conversation()
        conv.add_message(SystemMessage(content=system_context))
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await leptonai_model.abatch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
