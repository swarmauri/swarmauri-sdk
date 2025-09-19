import pytest

from swarmauri_embedding_nmf import NmfEmbedding


documents = [
    "This is the first document",
    "This is the second document",
    "And this is the third one",
]


@pytest.mark.example
def test_readme_usage_example() -> None:
    embedder = NmfEmbedding(n_components=3)

    vectors = embedder.fit_transform(documents)

    assert len(vectors) == len(documents)
    assert all(len(vector.value) == embedder.n_components for vector in vectors)
    assert embedder.extract_features()

    new_vector = embedder.infer_vector("This is a new document")
    assert len(new_vector.value) == embedder.n_components
