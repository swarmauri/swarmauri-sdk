import os
from swarmauri.standard.models.concrete.AnthropicModel import AnthropicModel
from swarmauri.standard.conversations.concrete.SimpleConversation import SimpleConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage

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
        assert type(model.predict(messages=conversation.as_messages())) == str
    test()