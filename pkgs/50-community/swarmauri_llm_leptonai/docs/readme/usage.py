import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = LeptonAIModel(
    api_key=os.environ["LEPTON_API_KEY"],
    name="llama3-8b",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
print(result.get_last().usage.total_tokens)
