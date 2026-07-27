
from pydantic import BaseModel, Field
from swarmauri_core.vector_stores.IPersistentVectorStore import (
    IPersistentVectorStore,
)


class VectorStorePersistentMixin(IPersistentVectorStore, BaseModel):
    """
    Mixin class for persistent-based vector stores.
    """

    collection_name: str

    collection: object | None = Field(
        None,
        description=(
            "Collection object for interacting with the persistent-based store"
        ),
    )

    path: str | None = Field(
        None, description="URL of the persistent-based store to connect to"
    )

    vector_size: int | None = Field(
        None, description="Size of the vectors used in the store"
    )
    client: object | None = Field(
        None,
        description=(
            "Client object for interacting with the persistent-based store"
        ),
    )

    vectorizer: object | None = Field(
        None,
        description="Vectorizer object for converting documents to vectors",
    )
