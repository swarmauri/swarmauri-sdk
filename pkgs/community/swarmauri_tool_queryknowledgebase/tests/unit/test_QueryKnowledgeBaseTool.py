from dataclasses import dataclass, field

import pytest

from swarmauri_tool_queryknowledgebase import QueryKnowledgeBaseTool


@dataclass
class Document:
    content: str
    metadata: dict = field(default_factory=dict)
    score: float | None = None


class KnowledgeBase:
    def __init__(self, items):
        self.items = items
        self.calls = []

    def retrieve(self, query, top_k=5):
        self.calls.append((query, top_k))
        return self.items[:top_k]


def test_retrieves_ranked_structured_results():
    store = KnowledgeBase(
        [Document("alpha", {"tag": "a"}, 0.9), Document("beta", {"tag": "b"}, 0.8)]
    )
    result = QueryKnowledgeBaseTool(knowledge_base=store)("topic", top_k=2)
    assert [item["content"] for item in result] == ["alpha", "beta"]
    assert [item["rank"] for item in result] == [1, 2]
    assert result[0]["score"] == 0.9


def test_filters_metadata_and_refills_top_k():
    store = KnowledgeBase(
        [
            Document("skip", {"tag": "b"}),
            Document("one", {"tag": "a"}),
            Document("two", {"tag": "a"}),
        ]
    )
    result = QueryKnowledgeBaseTool(knowledge_base=store)(
        "topic", top_k=2, metadata_filter={"tag": "a"}
    )
    assert [item["content"] for item in result] == ["one", "two"]
    assert store.calls == [("topic", 10)]


@pytest.mark.parametrize("query,top_k", [("", 5), ("ok", 0), ("ok", 101)])
def test_rejects_invalid_inputs(query, top_k):
    with pytest.raises(ValueError):
        QueryKnowledgeBaseTool(knowledge_base=KnowledgeBase([]))(query, top_k=top_k)


def test_serialization_excludes_runtime_adapter():
    tool = QueryKnowledgeBaseTool(knowledge_base=KnowledgeBase([]))
    restored = QueryKnowledgeBaseTool.model_validate_json(tool.model_dump_json())
    assert restored.id == tool.id
    assert restored.knowledge_base is None
