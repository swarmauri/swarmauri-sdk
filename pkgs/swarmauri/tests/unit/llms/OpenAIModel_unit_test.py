import pytest
import os
from swarmauri.llms.concrete.OpenAIModel import OpenAIModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage

API_KEY = os.getenv("OPENAI_API_KEY")


@pytest.fixture(scope="module")
def openai_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.mark.unit
def test_ubc_resource(openai_model):
    assert openai_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(openai_model):
    assert openai_model.type == "OpenAIModel"


@pytest.mark.unit
def test_serialization(openai_model):
    assert openai_model.id == LLM.model_validate_json(openai_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(openai_model):
    assert openai_model.name == "gpt-3.5-turbo"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(openai_model, model_name):
    model = openai_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(openai_model, model_name):
    model = openai_model
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
