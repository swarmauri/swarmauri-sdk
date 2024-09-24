import pytest
import os
from swarmauri.llms.concrete.MistralModel import MistralModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def mistral_model():
    API_KEY = os.getenv("MISTRAL_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(mistral_model):
    assert mistral_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(mistral_model):
    assert mistral_model.type == "MistralModel"


@pytest.mark.unit
def test_serialization(mistral_model):
    assert (
        mistral_model.id == LLM.model_validate_json(mistral_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(mistral_model):
    assert mistral_model.name == "open-mixtral-8x7b"


@pytest.mark.unit
def test_no_system_context(mistral_model):
    model = mistral_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.unit
def test_preamble_system_context(mistral_model):
    model = mistral_model  # Use the fixture

    conversation = Conversation()
    system_context = 'You only respond with the following phrase, "Jeff"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content

    assert type(prediction) == str
    assert "Jeff" in prediction
