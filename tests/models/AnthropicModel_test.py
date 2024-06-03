import os
from swarmauri.standard.models.concrete.AnthropicModel import AnthropicModel
from swarmauri.standard.conversations.concrete.SimpleConversation import SimpleConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

def test_initialization():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        model = AnthropicModel(api_key = API_KEY)
        assert model.model_name == 'claude-3-haiku-20240307'
    test()

def test_call():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        conversation = SimpleConversation()


        input_data = "Hello"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        model = AnthropicModel(api_key = API_KEY)
        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
    test()

def test_preamble_system_context():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        conversation = SimpleConversation()


        system_context = 'Your name is Jeff'
        human_message = SystemMessage(input_data)
        conversation.add_message(human_message)

        input_data = "Hello, what is your name?"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        model = AnthropicModel(api_key = API_KEY)
        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
        assert 'Jeff' in prediction
    test()

def test_multiple_system_contexts():
    def test():
        API_KEY = os.getenv('ANTHROPIC_API_KEY')
        conversation = SimpleConversation()


        system_context = 'Your name is Jeff'
        human_message = SystemMessage(input_data)
        conversation.add_message(human_message)

        input_data = "Hello"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        system_context = 'Your name is Ben'
        human_message = SystemMessage(input_data)
        conversation.add_message(human_message)

        input_data = "What is your name?"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        model = AnthropicModel(api_key = API_KEY)
        prediction = model.predict(messages=conversation.as_messages())
        assert type(prediction) == str
        assert 'Ben' in prediction
    test()