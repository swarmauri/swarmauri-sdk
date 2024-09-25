import pytest
import os
from swarmauri.llms.concrete.DeepSeekModel import DeepSeekModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def deepseek_model():
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.unit
def test_ubc_resource(deepseek_model):
    assert deepseek_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(deepseek_model):
    assert deepseek_model.type == "DeepSeekModel"


@pytest.mark.unit
def test_serialization(deepseek_model):
    assert (
        deepseek_model.id
        == LLM.model_validate_json(deepseek_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(deepseek_model):
    assert deepseek_model.name == "deepseek-chat"


@pytest.mark.unit
def test_no_system_context(deepseek_model):
    model = deepseek_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.unit
def test_preamble_system_context(deepseek_model):
    model = deepseek_model
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
