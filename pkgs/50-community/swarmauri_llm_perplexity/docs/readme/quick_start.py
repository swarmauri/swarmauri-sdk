import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
