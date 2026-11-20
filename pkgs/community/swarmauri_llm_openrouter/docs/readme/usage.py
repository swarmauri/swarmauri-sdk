from swarmauri_llm_openrouter import OpenRouterModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Explain provider routing."))
model = OpenRouterModel(
    api_key="...",
    name="openai/gpt-4o-mini",
    allowed_models=["openai/gpt-4o-mini"],
    app_name="My Swarmauri application",
)
model.predict(conversation, temperature=0.2)
print(conversation.get_last().content)
