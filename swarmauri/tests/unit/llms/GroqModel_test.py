import pytest
import os
from swarmauri.standard.llms.concrete.GroqModel import GroqModel as LLM
from swarmauri.standard.conversations.concrete.Conversation import Conversation

from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_ubc_resource():
    API_KEY = os.getenv("GROQ_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.resource == "LLM"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_ubc_type():
    API_KEY = os.getenv("GROQ_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.type == "GroqModel"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_serialization():
    API_KEY = os.getenv("GROQ_API_KEY")
    llm = LLM(api_key=API_KEY)
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_default_name():
    API_KEY = os.getenv("GROQ_API_KEY")
    model = LLM(api_key=API_KEY)
    assert model.name == "gemma-7b-it"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_no_system_context():
    API_KEY = os.getenv("GROQ_API_KEY")
    model = LLM(api_key=API_KEY)
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="Skipping due to environment variable not set"
)
def test_preamble_system_context():
    API_KEY = os.getenv("GROQ_API_KEY")
    model = LLM(api_key=API_KEY)
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
