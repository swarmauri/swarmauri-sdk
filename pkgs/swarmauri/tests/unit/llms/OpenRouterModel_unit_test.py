import pytest
import os
from swarmauri.llms.concrete.OpenRouterModel import OpenRouterModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


@pytest.fixture(scope="module")
def openrouter_model():
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
def test_ubc_resource(openrouter_model):
    assert openrouter_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(openrouter_model):
    assert openrouter_model.type == "OpenRouterModel"


@pytest.mark.unit
def test_serialization(openrouter_model):
    assert (
        openrouter_model.id
        == LLM.model_validate_json(openrouter_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(openrouter_model):
    assert openrouter_model.name == "01-ai/yi-34b"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(openrouter_model, model_name):
    model = openrouter_model
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
def test_preamble_system_context(openrouter_model, model_name):
    model = openrouter_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    try:
        model.predict(conversation=conversation)
        prediction = conversation.get_last().content
        assert isinstance(prediction, str)
        assert "Jeff" in prediction
    except Exception as e:
        pytest.fail(f"Error: {e}")
        # pytest.skip(f"Error: {e}")
