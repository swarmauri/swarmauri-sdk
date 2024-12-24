from typing import Optional
from pydantic import Field

from swarmauri_core.vector_stores.IPersistentVectorStore import IPersistentVectorStore


class VectorStorePersistentMixin(IPersistentVectorStore):
    """
    Mixin class for persistent-based vector stores.
    """

    collection_name: str

    collection: Optional[object] = Field(
        None,
        description="Collection object for interacting with the persistent-based store",
    )

    path: Optional[str] = Field(
        None, description="URL of the persistent-based store to connect to"
    )

    vector_size: Optional[int] = Field(
        None, description="Size of the vectors used in the store"
    )
    client: Optional[object] = Field(
        None,
        description="Client object for interacting with the persistent-based store",
    )

    vectorizer: Optional[object] = Field(
        None, description="Vectorizer object for converting documents to vectors"
    )