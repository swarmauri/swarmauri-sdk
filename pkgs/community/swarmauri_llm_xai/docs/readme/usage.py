import os

from swarmauri_llm_xai import XAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="Explain orbital mechanics briefly.")]
)
model = XAIModel(api_key=os.environ["XAI_API_KEY"], name="grok-4.3")
model.predict(conversation)
print(conversation.get_last().content)
