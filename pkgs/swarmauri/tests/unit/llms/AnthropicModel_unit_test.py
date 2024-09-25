import pytest
import os
from swarmauri.llms.concrete.AnthropicModel import AnthropicModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def anthropic_model():
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(anthropic_model):
    assert anthropic_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(anthropic_model):
    assert anthropic_model.type == "AnthropicModel"


@pytest.mark.unit
def test_serialization(anthropic_model):
    assert (
        anthropic_model.id
        == LLM.model_validate_json(anthropic_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(anthropic_model):
    assert anthropic_model.name == "claude-3-haiku-20240307"


@pytest.mark.unit
def test_no_system_context(anthropic_model):
    model = anthropic_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.unit
def test_preamble_system_context(anthropic_model):
    model = anthropic_model
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
