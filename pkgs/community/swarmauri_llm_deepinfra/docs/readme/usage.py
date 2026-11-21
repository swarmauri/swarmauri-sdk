import os

from swarmauri_llm_deepinfra import DeepInfraModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is DeepInfra?"))

model = DeepInfraModel(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="Qwen/Qwen2.5-72B-Instruct",
)
result = model.predict(
    conversation=conversation, temperature=0.2, max_tokens=256
)

print(result.get_last().content)
