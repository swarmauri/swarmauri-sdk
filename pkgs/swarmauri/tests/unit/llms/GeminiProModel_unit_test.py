import pytest
import os
from swarmauri.llms.concrete.GeminiProModel import GeminiProModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def geminipro_model():
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(geminipro_model):
    assert geminipro_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(geminipro_model):
    assert geminipro_model.type == "GeminiProModel"


@pytest.mark.unit
def test_serialization(geminipro_model):
    assert (
        geminipro_model.id
        == LLM.model_validate_json(geminipro_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(geminipro_model):
    assert geminipro_model.name == "gemini-1.5-pro-latest"


@pytest.mark.unit
def test_no_system_context(geminipro_model):
    model = geminipro_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(conversation=conversation).get_last().content
    assert type(prediction) == str


@pytest.mark.unit
def test_preamble_system_context(geminipro_model):
    model = geminipro_model
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
