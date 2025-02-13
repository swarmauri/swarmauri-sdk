import pytest
import os
from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.vector_stores.TfidfVectorStore import TfidfVectorStore
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.agents.RagAgent import RagAgent
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


@pytest.mark.unit
def test_agent_exec(rag_agent):
    result = rag_agent.exec("Hello")
    assert isinstance(result, str)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_aexec(rag_agent):
    result = await rag_agent.aexec("Hello")
    assert isinstance(result, str)
