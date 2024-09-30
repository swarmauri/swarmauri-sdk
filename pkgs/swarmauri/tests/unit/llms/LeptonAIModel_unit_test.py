import pytest
import os
from swarmauri.llms.concrete.LeptonAIModel import LeptonAIModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete.AgentMessage import AgentMessage
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage


@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_ubc_resource():
    API_KEY = os.getenv('LEPTON_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.resource == 'LLM'

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_ubc_type():
    API_KEY = os.getenv('LEPTON_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.type == 'LeptonAIModel'

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_serialization():
    API_KEY = os.getenv('LEPTON_API_KEY')
    llm = LLM(api_key = API_KEY)
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_default_name():
    API_KEY = os.getenv('LEPTON_API_KEY')
    model = LLM(api_key = API_KEY)
    assert model.name == 'llama3-8b'

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_no_system_context():
    API_KEY = os.getenv('LEPTON_API_KEY')
    model = LLM(api_key = API_KEY)
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.acceptance
def test_nonpreamble_system_context():
    API_KEY = os.getenv('LEPTON_API_KEY')
    model = LLM(api_key = API_KEY)
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
    assert 'Jeff' in prediction


@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_preamble_system_context():
    API_KEY = os.getenv('LEPTON_API_KEY')
    model = LLM(api_key = API_KEY)
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
    assert 'Jeff' in prediction

@pytest.mark.skipif(not os.getenv('LEPTON_API_KEY'), reason="Skipping due to environment variable not set")
@pytest.mark.acceptance
def test_multiple_system_contexts():
    API_KEY = os.getenv('LEPTON_API_KEY')
    model = LLM(api_key = API_KEY)
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
    assert type(prediction) == str
    assert 'Ben' in prediction
