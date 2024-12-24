from typing import Optional
from pydantic import Field

from swarmauri_core.vector_stores.ICloudVectorStore import ICloudVectorStore


class VectorStoreCloudMixin(ICloudVectorStore):
    """
    Mixin class for cloud-based vector stores.
    """

    api_key: str
    collection_name: str
    url: Optional[str] = Field(
        None, description="URL of the cloud-based store to connect to"
    )

    vector_size: Optional[int] = Field(
        None, description="Size of the vectors used in the store"
    )
    client: Optional[object] = Field(
        None, description="Client object for interacting with the cloud-based store"
    )