import pytest
import os
from swarmauri.llms.concrete.CohereModel import CohereModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("COHERE_API_KEY")


@pytest.fixture(scope="module")
def cohere_model():
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
def test_ubc_resource(cohere_model):
    assert cohere_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(cohere_model):
    assert cohere_model.type == "CohereModel"


@pytest.mark.unit
def test_serialization(cohere_model):
    assert cohere_model.id == LLM.model_validate_json(cohere_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(cohere_model):
    assert cohere_model.name == "command"


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_no_system_context(cohere_model, model_name):
    model = cohere_model
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
def test_preamble_system_context(cohere_model, model_name):
    model = cohere_model
    model.name = model_name

    conversation = Conversation()

    system_context = "Jane knows Martin."
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Who does Jane know?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "martin" in prediction.lower()
