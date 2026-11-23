import os

from swarmauri_llm_cloudflare import CloudflareWorkersAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="Explain edge inference.")]
)
model = CloudflareWorkersAIModel(
    account_id=os.environ["CLOUDFLARE_ACCOUNT_ID"],
    api_key=os.environ["CLOUDFLARE_API_TOKEN"],
    name="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
)
model.predict(conversation)
print(conversation.get_last().content)
