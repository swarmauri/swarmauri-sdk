import pytest
import os
from swarmauri.standard.llms.concrete.GeminiProModel import GeminiProModel as LLM
from swarmauri.standard.conversations.concrete.Conversation import Conversation

from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

@pytest.mark.unit
def test_ubc_resource():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.resource == 'LLM'

@pytest.mark.unit
def test_ubc_type():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.type == 'GeminiProModel'

@pytest.mark.unit
def test_serialization():
    API_KEY = os.getenv('GEMINI_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id

@pytest.mark.unit
def test_default_name():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    assert model.name == 'gemini-1.5-pro-latest'

@pytest.mark.unit
def test_no_system_context():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(messages=conversation.history)
    assert type(prediction) == str

@pytest.mark.acceptance
def test_nonpreamble_system_context():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    conversation = Conversation()

    # Say hi
    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    # Get Prediction
    prediction = model.predict(messages=conversation.history)
    conversation.add_message(AgentMessage(content=prediction))

    # Give System Context
    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    # Prompt
    input_data = "Hello Again."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)


    prediction_2 = model.predict(messages=conversation.history)
    assert type(prediction_2) == str
    assert 'Jeff' in prediction_2

@pytest.mark.unit
def test_preamble_system_context():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(messages=conversation.history)
    assert type(prediction) == str
    assert 'Jeff' in prediction

@pytest.mark.acceptance
def test_multiple_system_contexts():
    API_KEY = os.getenv('GEMINI_API_KEY')
    model = LLM(api_key = API_KEY)
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    prediction = model.predict(messages=conversation.history)
    conversation.add_message(AgentMessage(content=prediction))

    system_context_2 = 'You only respond with the following phrase, "Ben"'
    human_message = SystemMessage(content=system_context_2)
    conversation.add_message(human_message)

    input_data_2 = "Hey"
    human_message = HumanMessage(content=input_data_2)
    conversation.add_message(human_message)

    prediction = model.predict(messages=conversation.history)
    assert type(prediction) == str
    assert 'Ben' in prediction