from swarmauri_base.vector_stores.VectorStoreComparator import (
    SimilarityVectorStoreComparator,
)
from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity


class CosineSimilarityComparator(SimilarityVectorStoreComparator):
    """Default dense-vector comparator for Swarmauri vector stores."""

    def __init__(self):
        super().__init__(CosineSimilarity())
