import pytest
import os
from swarmauri.standard.models.concrete.AnthropicModel import AnthropicModel
from swarmauri.standard.conversations.concrete.SimpleConversation import SimpleConversation

from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

@pytest.mark.unit
def test_initialization():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        assert model.model_name == 'claude-3-haiku-20240307'
    test()

@pytest.mark.unit
def test_no_system_context():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        conversation = SimpleConversation()

        input_data = "Hello"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
    test()

@pytest.mark.unit
def test_nonpreamble_system_context():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        conversation = SimpleConversation()

        # Say hi
        input_data = "Hi"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        # Get Prediction
        prediction = model.predict(messages=conversation.as_messages())
        conversation.add_message(AgentMessage(prediction))

        # Give System Context
        system_context = 'You only respond with the following phrase, "Jeff"'
        human_message = SystemMessage(system_context)
        conversation.add_message(human_message)

        # Prompt
        input_data = "Hello Again."
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        
        prediction_2 = model.predict(messages=conversation.as_messages())
        assert type(prediction_2) == str
        assert 'Jeff' in prediction_2
    test()


@pytest.mark.unit
def test_preamble_system_context():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        conversation = SimpleConversation()

        system_context = 'You only respond with the following phrase, "Jeff"'
        human_message = SystemMessage(system_context)
        conversation.add_message(human_message)

        input_data = "Hi"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
        assert 'Jeff' in prediction
    test()

@pytest.mark.acceptance
def test_multiple_system_contexts():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        conversation = SimpleConversation()

        system_context = 'You only respond with the following phrase, "Jeff"'
        human_message = SystemMessage(system_context)
        conversation.add_message(human_message)

        input_data = "Hi"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        prediction = model.predict(messages=conversation.as_messages())
        conversation.add_message(AgentMessage(prediction))

        system_context_2 = 'You only respond with the following phrase, "Ben"'
        human_message = SystemMessage(system_context_2)
        conversation.add_message(human_message)

        input_data_2 = "Hey"
        human_message = HumanMessage(input_data_2)
        conversation.add_message(human_message)

        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
        assert 'Ben' in prediction
    test()