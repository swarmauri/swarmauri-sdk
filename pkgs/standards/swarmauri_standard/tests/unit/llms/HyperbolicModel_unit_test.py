import logging
import pytest
import os

from swarmauri.llms.concrete.HyperbolicModel import HyperbolicModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage

from swarmauri.messages.concrete.AgentMessage import UsageData

from swarmauri.utils.timeout_wrapper import timeout

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HYPERBOLIC_API_KEY")


@pytest.fixture(scope="module")
def hyperbolic_model():
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
def test_ubc_resource(hyperbolic_model):
    assert hyperbolic_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(hyperbolic_model):
    assert hyperbolic_model.type == "HyperbolicModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(hyperbolic_model):
    assert (
        hyperbolic_model.id
        == LLM.model_validate_json(hyperbolic_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(hyperbolic_model):
    assert hyperbolic_model.name == "meta-llama/Meta-Llama-3.1-8B-Instruct"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(hyperbolic_model, model_name):
    model = hyperbolic_model
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
def test_preamble_system_context(hyperbolic_model, model_name):
    model = hyperbolic_model
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
    usage_data = conversation.get_last().usage

    logging.info(usage_data)

    assert type(prediction) is str
    assert "Jeff" in prediction
    assert isinstance(usage_data, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(hyperbolic_model, model_name):
    model = hyperbolic_model
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
    assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(hyperbolic_model, model_name):
    model = hyperbolic_model
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
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_astream(hyperbolic_model, model_name):
    model = hyperbolic_model
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


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(hyperbolic_model, model_name):
    model = hyperbolic_model
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
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_abatch(hyperbolic_model, model_name):
    model = hyperbolic_model
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
