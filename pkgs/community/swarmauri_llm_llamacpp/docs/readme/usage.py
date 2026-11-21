from swarmauri_llm_llamacpp import LlamaCppModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Explain Swarmauri in one paragraph.")
)

model = LlamaCppModel()
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
