import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.conversations.concrete.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from swarmauri.documents.concrete.Document import Document
from swarmauri.agents.concrete import RagAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def rag_agent():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")

    llm = GroqModel(api_key=API_KEY)
    system_context = SystemMessage(content="Your name is Jeff.")
    conversation = MaxSystemContextConversation(
        system_context=system_context, max_size=4
    )
    vector_store = TfidfVectorStore()

    documents = [
        Document(content="Their sister's name is Jane."),
        Document(content="Their mother's name is Jean."),
        Document(content="Their father's name is Joseph."),
        Document(content="Their grandfather's name is Alex."),
    ]
    vector_store.add_documents(documents)

    agent = RagAgent(
        llm=llm,
        conversation=conversation,
        system_context=system_context,
        vector_store=vector_store,
    )
    return agent


@pytest.mark.unit
def test_ubc_resource(rag_agent):
    assert rag_agent.resource == "Agent"


@pytest.mark.unit
def test_ubc_type(rag_agent):
    assert rag_agent.type == "RagAgent"


@pytest.mark.unit
def test_serialization(rag_agent):
    assert rag_agent.id == RagAgent.model_validate_json(rag_agent.model_dump_json()).id
