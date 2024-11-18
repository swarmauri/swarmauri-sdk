import json
import logging

import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

from swarmauri.messages.concrete.AgentMessage import UsageData
from swarmauri.utils.timeout_wrapper import timeout


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
# image_path = "/home/michaeldecent/Downloads/carbon.png"
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"


@timeout(5)
@pytest.fixture(scope="module")
def groq_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@timeout(5)
@pytest.fixture(scope="module")
def llama_guard_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    llm.name = "llama-guard-3-8b"
    return llm


@timeout(5)
def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)

    # not consistent with their results
    failing_llms = [
        "llama3-70b-8192",
        "llama-3.2-90b-text-preview",
        "mixtral-8x7b-32768",
        "llava-v1.5-7b-4096-preview",
        "llama-guard-3-8b",
    ]

    # Filter out the failing models
    allowed_models = [
        model
        for model in llm.allowed_models
        if model not in failing_llms
    ]

    return allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(groq_model):
    assert groq_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(groq_model):
    assert groq_model.type == "GroqModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(groq_model):
    assert groq_model.id == LLM.model_validate_json(groq_model.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_default_name(groq_model):
    assert groq_model.name == "gemma-7b-it"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(groq_model, model_name):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    logging.info(usage_data)
    assert type(prediction) is str
    assert isinstance(usage_data, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(groq_model, model_name):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"

    human_message = HumanMessage(content=json.dumps(input_data))
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    logging.info(usage_data)
    assert type(prediction) is str
    assert isinstance(usage_data, UsageData)


@timeout(5)
@pytest.mark.unit
def test_llama_guard_3_8b_no_system_context(llama_guard_model):
    """
    Test case specifically for the llama-guard-3-8b model.
    This model is designed to classify inputs as safe or unsafe.

    Reference: https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-3/
    """
    conversation = Conversation()

    input_data = "Hello, how are you?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    llama_guard_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    assert type(prediction) is str
    assert isinstance(usage_data, UsageData)
    assert "safe" in prediction.lower()


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(groq_model, model_name):
    model = groq_model
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
    # assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(groq_model, model_name):
    model = groq_model
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
async def test_apredict(groq_model, model_name):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_astream(groq_model, model_name):
    model = groq_model
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
    # assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(groq_model, model_name):
    model = groq_model
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
