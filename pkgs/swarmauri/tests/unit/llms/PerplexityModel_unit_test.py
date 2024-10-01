import pytest
import os
from swarmauri.llms.concrete.PerplexityModel import PerplexityModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")


@pytest.fixture(scope="module")
def perplexity_model():
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
def test_ubc_resource(perplexity_model):
    assert perplexity_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(perplexity_model):
    assert perplexity_model.type == "PerplexityModel"


@pytest.mark.unit
def test_serialization(perplexity_model):
    assert (
        perplexity_model.id
        == LLM.model_validate_json(perplexity_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(perplexity_model):
    assert perplexity_model.name == "llama-3.1-70b-instruct"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(perplexity_model, model_name):
    model = perplexity_model
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
def test_preamble_system_context(perplexity_model, model_name):
    model = perplexity_model
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
