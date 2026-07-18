from swarmauri_base.retrievers.RetrieverMixin import RetrieverMixin
from swarmauri_core.vector_stores.IVectorStoreRetrieve import (
    IVectorStoreRetrieve,
)


class VectorStoreRetrieveMixin(IVectorStoreRetrieve, RetrieverMixin):
    """Compatibility mixin for vector stores that support retrieval."""
