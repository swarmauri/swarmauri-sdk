from swarmauri_llm_nvidia_nim import NvidiaNIMModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="What is accelerated computing?")]
)
model = NvidiaNIMModel(
    base_url="http://localhost:8000",
    name="meta/llama-3.1-8b-instruct",
)
model.predict(conversation)
print(conversation.get_last().content)
