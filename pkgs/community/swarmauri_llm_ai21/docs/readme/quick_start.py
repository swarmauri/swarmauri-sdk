import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(
    HumanMessage(content="What is a Swarmauri component?")
)

model = AI21StudioModel(
    api_key=os.environ["AI21STUDIO_API_KEY"],
    name="jamba-mini",
)
result = model.predict(
    conversation=conversation, temperature=0.3, max_tokens=256
)

print(result.get_last().content)
