import os

from swarmauri_llm_openai import OpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = OpenAIModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
