import os

from swarmauri_llm_azureopenai import AzureOpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="Summarize this release.")]
)
model = AzureOpenAIModel(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    name="my-gpt-deployment",
)
model.predict(conversation)
print(conversation.get_last().content)
