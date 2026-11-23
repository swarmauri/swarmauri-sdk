import os

from swarmauri_llm_mistral import MistralModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = MistralModel(
    api_key=os.environ["MISTRAL_API_KEY"],
    name="mistral-medium-2508",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
