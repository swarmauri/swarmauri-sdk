from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize this deployment risk.")
)

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
