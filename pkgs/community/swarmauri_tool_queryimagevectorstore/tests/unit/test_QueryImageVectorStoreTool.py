import pytest

from swarmauri_tool_queryimagevectorstore import QueryImageVectorStoreTool


class Embedder:
    def infer_vector(self, image):
        assert image == {"pixels": [1, 2]}
        return [0.1, 0.2]


class Store:
    def __init__(self):
        self.calls = []

    def retrieve_by_vector(self, embedding, top_k=5):
        self.calls.append((embedding, top_k))
        return [
            {"id": "skip", "score": 0.99, "metadata": {"kind": "dog"}},
            {"id": "one", "score": 0.90, "metadata": {"kind": "cat"}},
            {"id": "two", "score": 0.80, "metadata": {"kind": "cat"}},
        ]


def test_queries_with_precomputed_embedding():
    store = Store()
    result = QueryImageVectorStoreTool(vector_store=store)(
        embedding=[0.1, 0.2], top_k=2
    )
    assert [item["id"] for item in result] == ["skip", "one"]
    assert store.calls == [([0.1, 0.2], 2)]


def test_embeds_image_and_filters_results():
    store = Store()
    tool = QueryImageVectorStoreTool(vector_store=store, image_embedder=Embedder())
    result = tool(image={"pixels": [1, 2]}, top_k=2, metadata_filter={"kind": "cat"})
    assert [item["id"] for item in result] == ["one", "two"]
    assert [item["rank"] for item in result] == [1, 2]
    assert store.calls == [([0.1, 0.2], 10)]


@pytest.mark.parametrize(
    "kwargs", [{}, {"image": "x", "embedding": [1.0]}, {"embedding": []}]
)
def test_rejects_ambiguous_or_empty_input(kwargs):
    with pytest.raises((ValueError, TypeError)):
        QueryImageVectorStoreTool(vector_store=Store(), image_embedder=Embedder())(
            **kwargs
        )


def test_serialization_excludes_runtime_adapters():
    tool = QueryImageVectorStoreTool(vector_store=Store(), image_embedder=Embedder())
    restored = QueryImageVectorStoreTool.model_validate_json(tool.model_dump_json())
    assert restored.id == tool.id
    assert restored.vector_store is None
    assert restored.image_embedder is None
