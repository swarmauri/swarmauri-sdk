from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a one-sentence release note.")
)

model = GroqModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, max_tokens=120)

print(result.get_last().content)
