import pytest
import os
from swarmauri.llms.concrete.CohereModel import CohereModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def cohere_model():
    API_KEY = os.getenv("COHERE_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.acceptance
def test_multiple_system_contexts(cohere_model):
    model = cohere_model
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(conversation=conversation)

    system_context_2 = 'You only respond with the following phrase, "Ben"'
    human_message = SystemMessage(content=system_context_2)
    conversation.add_message(human_message)

    input_data_2 = "Hey"
    human_message = HumanMessage(content=input_data_2)
    conversation.add_message(human_message)

    model.predict(conversation=conversation, temperature=0)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "Ben" in prediction
