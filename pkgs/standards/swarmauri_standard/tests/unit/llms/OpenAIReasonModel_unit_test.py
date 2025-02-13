import logging
import pytest
import os

from swarmauri_standard.llms.OpenAIReasonModel import OpenAIReasonModel as LLM
from swarmauri_standard.conversations.Conversation import Conversation

from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

from swarmauri_standard.messages.AgentMessage import UsageData

from swarmauri_standard.utils.timeout_wrapper import timeout

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


@pytest.fixture(scope="module")
def openai_reason_model():
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
def test_ubc_resource(openai_reason_model):
    assert openai_reason_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(openai_reason_model):
    assert openai_reason_model.type == "OpenAIReasonModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(openai_reason_model):
    assert (
        openai_reason_model.id
        == LLM.model_validate_json(openai_reason_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(openai_reason_model):
    assert openai_reason_model.name == "o1"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(openai_reason_model, model_name):
    model = openai_reason_model
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
@pytest.mark.unit
def test_preamble_system_context(openai_reason_model):
    model = openai_reason_model
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.name = "o1"
    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    assert type(prediction) is str
    assert "Jeff" in prediction
    assert isinstance(usage_data, UsageData)

    model.name = "o1-mini"
    with pytest.raises(
        ValueError, match="System messages are not allowed for models other than 'o1'."
    ):
        model.predict(conversation=conversation)
        prediction = conversation.get_last().content
        usage_data = conversation.get_last().usage
        assert isinstance(usage_data, UsageData)


@timeout(5)
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
async def test_apredict(openai_reason_model, model_name):
    model = openai_reason_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)
    assert isinstance(conversation.get_last().usage, UsageData)
