import pytest

from swarmauri_standard.documents.Document import Document
from swarmauri_tool_addcontenttorag.AddContentToRAGTool import (
    AddContentToRAGTool as Tool,
)


class FakeKnowledgeBase:
    """Minimal stand-in for a store providing add_documents()."""

    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)


class AttributeOnlyStore:
    """Reads ``doc.content`` immediately, the way the standard stores do."""

    def __init__(self):
        self.contents = []

    def add_documents(self, documents):
        self.contents.extend(document.content for document in documents)


def _tool_with(store):
    tool = Tool()
    tool.knowledge_base = store
    return tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "AddContentToRAGTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_requires_a_knowledge_base():
    with pytest.raises(ValueError):
        Tool()(content="hello")


@pytest.mark.unit
def test_rejects_a_store_without_add_documents():
    tool = Tool()
    tool.knowledge_base = object()

    with pytest.raises(ValueError):
        tool(content="hello")


@pytest.mark.unit
def test_rejects_blank_content():
    store = FakeKnowledgeBase()
    tool = _tool_with(store)

    with pytest.raises(ValueError):
        tool(content="   \n\t ")

    assert store.documents == []


@pytest.mark.unit
def test_adds_content_to_the_store():
    store = FakeKnowledgeBase()
    tool = _tool_with(store)

    result = tool(content="alpha beta")

    assert result["added"] == 1
    assert result["content_length"] == len("alpha beta")
    assert len(store.documents) == 1
    assert store.documents[0].content == "alpha beta"
    assert store.documents[0].metadata == {}


@pytest.mark.unit
def test_passes_document_instances_not_mappings():
    """IVectorStore.add_documents takes IDocument, not dicts."""
    store = FakeKnowledgeBase()
    tool = _tool_with(store)

    tool(content="alpha")

    assert isinstance(store.documents[0], Document)


@pytest.mark.unit
def test_works_with_a_store_that_reads_attributes_immediately():
    """Matches TfidfVectorStore and friends, which evaluate doc.content."""
    store = AttributeOnlyStore()
    tool = _tool_with(store)

    tool(content="alpha")

    assert store.contents == ["alpha"]


@pytest.mark.unit
def test_passes_metadata_tags():
    store = FakeKnowledgeBase()
    tool = _tool_with(store)

    tool(content="alpha", metadata={"source": "handbook", "page": 4})

    assert store.documents[0].metadata == {
        "source": "handbook",
        "page": 4,
    }


@pytest.mark.unit
def test_does_not_share_the_caller_metadata_mapping():
    store = FakeKnowledgeBase()
    tool = _tool_with(store)
    tags = {"source": "handbook"}

    tool(content="alpha", metadata=tags)
    tags["source"] = "changed"

    assert store.documents[0].metadata["source"] == "handbook"


@pytest.mark.unit
def test_wraps_store_failures_without_leaking_details():
    class BrokenStore:
        def add_documents(self, documents):
            raise ConnectionError("host db.internal:5432 refused")

    tool = _tool_with(BrokenStore())

    with pytest.raises(RuntimeError) as excinfo:
        tool(content="alpha")

    assert "db.internal" not in str(excinfo.value)


@pytest.mark.unit
def test_knowledge_base_is_excluded_from_serialized_state():
    tool = _tool_with(FakeKnowledgeBase())

    assert "knowledge_base" not in tool.model_dump()
