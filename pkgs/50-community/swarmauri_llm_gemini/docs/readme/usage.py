from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a concise project status update.")
)

model = GeminiProModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
