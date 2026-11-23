import os

from swarmauri_llm_cohere import CohereModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Cohere Command A?"))

model = CohereModel(
    api_key=os.environ["COHERE_API_KEY"],
    name="command-a-03-2025",
)
result = model.predict(
    conversation=conversation, max_tokens=256, temperature=0.2
)

print(result.get_last().content)
