from pydantic import BaseModel, Field, SecretStr
from swarmauri_core.vector_stores.ICloudVectorStore import ICloudVectorStore


class VectorStoreCloudMixin(ICloudVectorStore, BaseModel):
    """
    Mixin class for cloud-based vector stores.
    """

    api_key: SecretStr | None = Field(
        None, description="API key for the cloud-based store"
    )
    collection_name: str
    url: str | None = Field(
        None, description="URL of the cloud-based store to connect to"
    )

    vector_size: int | None = Field(
        None, description="Size of the vectors used in the store"
    )
    client: object | None = Field(
        None,
        description="Client object for interacting with the cloud-based store",
    )
