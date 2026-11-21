from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize why OpenAI-compatible APIs are useful.")
)

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
