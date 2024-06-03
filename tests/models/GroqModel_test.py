import os
from swarmauri.standard.models.concrete.GroqModel import GroqModel
from swarmauri.standard.conversations.concrete.SimpleConversation import SimpleConversation

def test_initialization():
    def test():
    	GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        conversation = SimpleConversation()

        
        human_message = HumanMessage(input_data)
		conversation.add_message(human_message)

        model = GroqModel(api_key = GROQ_API_KEY)
        assert model.model_name == 'mixtral-8x7b-32768'
    test()

def test_call():
    def test():
    	GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        conversation = SimpleConversation()

        
        human_message = HumanMessage(input_data)
		conversation.add_message(human_message)

        model = GroqModel(api_key = GROQ_API_KEY)
        assert type(model.predict(messages=conversation.as_messages())) == str
    test()