import pytest
import os
from swarmauri_standard.llms.PerplexityModel import PerplexityModel as LLM
from swarmauri_standard.conversations.Conversation import Conversation

from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage


@pytest.fixture(scope="module")
def perplexity_model():
    API_KEY = os.getenv("PERPLEXITY_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.acceptance
def test_nonpreamble_system_context(perplexity_model):
    model = perplexity_model
    conversation = Conversation()

    # Say hi
    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    # Get Prediction
    model.predict(conversation=conversation)

    # Give System Context
    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    # Prompt
    input_data = "Hello Again."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert "Jeff" in prediction


@pytest.mark.xfail(reason="These models are expected to fail")
@pytest.mark.acceptance
def test_multiple_system_contexts(perplexity_model):
    model = perplexity_model
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

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) is str
    assert "Ben" in prediction
