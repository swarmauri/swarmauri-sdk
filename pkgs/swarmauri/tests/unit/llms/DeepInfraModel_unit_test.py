import pytest
import os
from swarmauri.llms.concrete.DeepInfraModel import DeepInfraModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def deepinfra_model():
    API_KEY = os.getenv("DEEPINFRA_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(deepinfra_model):
    assert deepinfra_model.resource == "deepinfra_model"


@pytest.mark.unit
def test_ubc_type(deepinfra_model):
    assert deepinfra_model.type == "DeepInfraModel"


@pytest.mark.unit
def test_serialization(deepinfra_model):
    assert (
        deepinfra_model.id
        == LLM.model_validate_json(deepinfra_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(deepinfra_model):
    assert deepinfra_model.name == "Qwen/Qwen2-72B-Instruct"


@pytest.mark.unit
def test_no_system_context(deepinfra_model):
    model = deepinfra_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) is str


@pytest.mark.unit
def test_preamble_system_context(deepinfra_model):
    model = deepinfra_model
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
