import os
import pytest

from swarmauri_standard.llms.GroqModel import GroqModel as LLM
from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.vector_stores.TfidfVectorStore import TfidfVectorStore
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.agents.RagAgent import RagAgent


@pytest.fixture(scope="module")
def groq_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.mark.integration
def test_agent_exec(groq_model):
    system_context = SystemMessage(content="Your name is Jeff.")
    conversation = MaxSystemContextConversation(
        system_context=system_context, max_size=4
    )
    vector_store = TfidfVectorStore()
    documents = [
        Document(content="Their sister's name is Jane."),
        Document(content="Their mother's name is Jean."),
        Document(content="Their father's name is Joseph."),
        Document(content="Their grandather's name is Alex."),
    ]
    vector_store.add_documents(documents)

    agent = RagAgent(
        llm=groq_model,
        conversation=conversation,
        system_context=system_context,
        vector_store=vector_store,
    )
    result = agent.exec("What is the name of their grandfather?")
    assert type(result) is str
