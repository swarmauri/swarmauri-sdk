import logging
import os

import httpx
import pytest

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.LlamaCppModel import LlamaCppModel as LLM
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

# Set up the base URL for tests
LLAMA_CPP_URL = os.getenv("LLAMA_CPP_URL", "http://localhost:8080/v1")


@pytest.fixture(scope="module")
def llama_server_available():
    """Check if LlamaCpp server is running and available"""
    try:
        response = httpx.get(f"{LLAMA_CPP_URL}/models", timeout=2.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False


@pytest.fixture(scope="module")
def llama_model(llama_server_available):
    if not llama_server_available:
        pytest.skip("Skipping due to LlamaCpp server not available")
    llm = LLM()
    return llm


def get_allowed_models(is_available=None):
    """Get allowed models if server is available"""
    if is_available is None:
        is_available = llama_server_available

    if not is_available:
        return []
    llm = LLM()
    return llm.allowed_models


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_resource(llama_model):
    assert llama_model.resource == "LLM"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_type(llama_model):
    assert llama_model.type == "LlamaCppModel"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_serialization(llama_model):
    assert llama_model.id == LLM.model_validate_json(llama_model.model_dump_json()).id


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_default_name(llama_model):
    assert llama_model.name == llama_model.allowed_models[0]


@pytest.mark.timeout(30)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_basic_prediction(llama_model, model_name):
    model = llama_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content

    assert type(prediction) is str
    assert len(prediction) > 0


@pytest.mark.timeout(30)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_system_prompt(llama_model, model_name):
    model = llama_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Hello World"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content

    assert type(prediction) is str
    assert "Hello World" in prediction


@pytest.mark.timeout(60)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(llama_model, model_name):
    model = llama_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Write a short story about a cat."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in model.stream(conversation=conversation):
        logging.info(token)
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.timeout(30)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(llama_model, model_name):
    model = llama_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)
    assert len(prediction) > 0


@pytest.mark.timeout(60)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(llama_model, model_name):
    model = llama_model
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


@pytest.mark.timeout(60)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(llama_model, model_name):
    model = llama_model
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
        assert len(result.get_last().content) > 0


@pytest.mark.timeout(60)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(llama_model, model_name):
    model = llama_model
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
        assert len(result.get_last().content) > 0


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_get_allowed_models(llama_model):
    models = llama_model.get_allowed_models()
    assert isinstance(models, list)
    assert len(models) > 0
    assert all(isinstance(model, str) for model in models)


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_message_formatting(llama_model):
    conversation = Conversation()
    conversation.add_message(SystemMessage(content="You are a helpful assistant"))
    conversation.add_message(HumanMessage(content="Hi there"))

    formatted = llama_model._format_messages(conversation.history)

    assert isinstance(formatted, list)
    assert len(formatted) == 2
    assert formatted[0]["role"] == "system"
    assert formatted[1]["role"] == "user"
