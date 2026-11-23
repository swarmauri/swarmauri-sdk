import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer in concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Swarmauri?"))

model = AnthropicModel(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    name="claude-sonnet-4-0",
)
result = model.predict(
    conversation=conversation, max_tokens=256, temperature=0.2
)

print(result.get_last().content)
