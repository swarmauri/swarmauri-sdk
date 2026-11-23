import pytest

from swarmauri_standard.documents.Document import Document
from swarmauri_standard.vector_stores.TfidfVectorStore import TfidfVectorStore


@pytest.mark.unit
def test_tfidf_vector_store_uses_descending_cosine_similarity():
    store = TfidfVectorStore()
    store.add_documents(
        [
            Document(id="alpha", content="apple banana"),
            Document(id="beta", content="carrot daikon"),
        ]
    )

    results = store.retrieve("apple", top_k=2)

    assert [document.id for document in results] == ["alpha", "beta"]
    assert store.comparator.ranking_direction == "descending"
