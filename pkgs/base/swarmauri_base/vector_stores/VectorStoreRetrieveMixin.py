from pydantic import BaseModel
from swarmauri_core.vector_stores.IVectorStoreRetrieve import (
    IVectorStoreRetrieve,
)


class VectorStoreRetrieveMixin(IVectorStoreRetrieve, BaseModel):
    """Compatibility mixin for vector stores that support retrieval."""
